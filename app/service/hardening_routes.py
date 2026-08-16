from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from one_advisory.failures import choose_contact_recovery, report_contact_failure, report_rescission_ambiguity, report_source_unavailable, restore_source
from one_advisory.store import MemoryIncidentStore
from one_advisory.wake_actions import AdvisoryWakeExecutor
from one_advisory.workflow import activate_fleet, approve_proposals, create_incident, public_view
from spine.clock import MemoryClockStateStore, SimulatedClock
from spine.wake import MemoryWakeStore, WakeScheduler


class HumanChoice(BaseModel):
    chosen_by: str = Field(min_length=3, max_length=140)


class Approval(BaseModel):
    approver: str = Field(min_length=3, max_length=140)


class Advance(BaseModel):
    minutes: int = Field(gt=0, le=10080)


def build_hardening_router(store, scheduler, clock):
    router = APIRouter(prefix="/api/hardening", tags=["one-advisory-hardening"])
    executor = AdvisoryWakeExecutor(store)

    def require(incident_id):
        incident = store.get(incident_id)
        if incident is None:
            raise HTTPException(404, f"no incident {incident_id}")
        return incident

    def mutate(incident_id, operation):
        incident = require(incident_id)
        try:
            operation(incident)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc
        store.put(incident)
        return public_view(incident)

    @router.post("/incidents/{incident_id}/source-unavailable")
    def source_unavailable(incident_id: str): return mutate(incident_id, report_source_unavailable)

    @router.post("/incidents/{incident_id}/restore-source")
    def source_restored(incident_id: str): return mutate(incident_id, restore_source)

    @router.post("/incidents/{incident_id}/approve-and-watch")
    def approve_and_watch(incident_id: str, request: Approval):
        incident = require(incident_id)
        try: approve_proposals(incident, request.approver)
        except ValueError as exc: raise HTTPException(409, str(exc)) from exc
        for facility in incident["facilities"]:
            scheduler.sleep_for(incident_id, "facility_ack_check", timedelta(minutes=20), {"facility_id": facility["facility_id"]}, facility["facility_id"])
        store.put(incident)
        return public_view(incident)

    @router.post("/incidents/{incident_id}/contact-failure")
    def contact_failure(incident_id: str): return mutate(incident_id, report_contact_failure)

    @router.post("/incidents/{incident_id}/choose-contact")
    def choose_contact(incident_id: str, request: HumanChoice): return mutate(incident_id, lambda row: choose_contact_recovery(row, request.chosen_by))

    @router.post("/incidents/{incident_id}/rescission-ambiguity")
    def rescission_ambiguity(incident_id: str): return mutate(incident_id, report_rescission_ambiguity)

    @router.get("/incidents/{incident_id}/wakes")
    def wakes(incident_id: str):
        require(incident_id)
        return {"wakes": [{"wake_id": w.wake_id, "kind": w.kind, "status": w.status.value, "attempts": w.attempts} for w in scheduler._store.for_run(incident_id)]}

    @router.post("/advance")
    def advance(request: Advance):
        now = clock.advance(timedelta(minutes=request.minutes))
        rows = scheduler.dispatch_due(executor.execute)
        return {"simulated": True, "now": now.isoformat(), "dispatched": [row.wake_id for row in rows]}

    @router.get("/proof")
    def proof():
        checks = []
        def check(name, value): checks.append({"check": name, "pass": bool(value)})
        incident = create_incident(); activate_fleet(incident); report_source_unavailable(incident)
        check("source loss blocks unsupported tasks", incident["status"] == "evidence_blocked" and incident["evidence_gate"]["system_authorization"] is None)
        restore_source(incident); approve_proposals(incident, "Jordan Lee - synthetic"); report_contact_failure(incident)
        school = next(row for row in incident["facilities"] if row["facility_id"] == "fac-school")
        check("contact failure invents no acknowledgement", school["response_state"] == "delivery_failed" and school["contact_recovery"]["external_contact_sent"] is False)
        choose_contact_recovery(incident, "Jordan Lee - synthetic")
        check("alternate route requires named human", school["contact_recovery"]["selected_by_ai"] is False and school["contact_recovery"]["selected_by"])
        local_store = MemoryIncidentStore(); timed = create_incident(); activate_fleet(timed); local_store.put(timed)
        local_clock = SimulatedClock(MemoryClockStateStore()); local_scheduler = WakeScheduler(MemoryWakeStore(), local_clock)
        first = local_scheduler.sleep_for(timed["incident_id"], "facility_ack_check", timedelta(minutes=20), discriminator="fac-school")
        second = local_scheduler.sleep_for(timed["incident_id"], "facility_ack_check", timedelta(minutes=20), discriminator="fac-school")
        check("wake registration is idempotent", first.wake_id == second.wake_id)
        local_clock.advance(timedelta(minutes=21)); fired = local_scheduler.dispatch_due(AdvisoryWakeExecutor(local_store).execute)
        check("ack wake fires exactly once", len(fired) == 1 and not local_scheduler.dispatch_due(AdvisoryWakeExecutor(local_store).execute))
        check("wake sends no external contact", local_store.get(timed["incident_id"])["wake_actions"][0]["external_contact"] is False)
        check("registered fleet retains explicit approvals", all("approval" in row for row in timed["registry"]))
        check("system never issues advisory", timed["safety"]["system_issued_advisory"] is False)
        return {"passed": sum(row["pass"] for row in checks), "total": len(checks), "checks": checks}

    return router

