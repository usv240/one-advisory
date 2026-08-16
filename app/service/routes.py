"""HTTP routes for the One Advisory response fleet."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from one_advisory.store import IncidentStore
from one_advisory.workflow import (
    activate_fleet,
    approve_proposals,
    create_incident,
    detect_resource_conflict,
    escalate_nonresponse,
    public_view,
    receive_facility_updates,
    reject_unregistered_action,
    rescind_and_recover,
    resolve_resource_conflict,
    run_full_demo,
)


class ApprovalRequest(BaseModel):
    approver: str = Field(min_length=3, max_length=140)


class AllocationRequest(BaseModel):
    option_id: str
    approver: str = Field(min_length=3, max_length=140)


def build_router(store: IncidentStore) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["one-advisory"])

    def require(incident_id: str) -> dict[str, Any]:
        incident = store.get(incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail=f"no incident {incident_id}")
        return incident

    def mutate(incident_id: str, operation: Any) -> dict[str, Any]:
        incident = require(incident_id)
        try:
            operation(incident)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        store.put(incident)
        return public_view(incident)

    @router.post("/incidents")
    def open_incident() -> dict[str, Any]:
        incident = create_incident()
        store.put(incident)
        return public_view(incident)

    @router.get("/incidents/{incident_id}")
    def get_incident(incident_id: str) -> dict[str, Any]:
        return public_view(require(incident_id))

    @router.post("/incidents/{incident_id}/activate")
    def activate(incident_id: str) -> dict[str, Any]:
        return mutate(incident_id, activate_fleet)

    @router.post("/incidents/{incident_id}/policy-test")
    def policy_test(incident_id: str) -> dict[str, Any]:
        return mutate(incident_id, reject_unregistered_action)

    @router.post("/incidents/{incident_id}/approve")
    def approve(incident_id: str, request: ApprovalRequest) -> dict[str, Any]:
        return mutate(incident_id, lambda incident: approve_proposals(incident, request.approver))

    @router.post("/incidents/{incident_id}/facility-updates")
    def facility_updates(incident_id: str) -> dict[str, Any]:
        return mutate(incident_id, receive_facility_updates)

    @router.post("/incidents/{incident_id}/detect-conflict")
    def conflict(incident_id: str) -> dict[str, Any]:
        return mutate(incident_id, detect_resource_conflict)

    @router.post("/incidents/{incident_id}/allocate")
    def allocate(incident_id: str, request: AllocationRequest) -> dict[str, Any]:
        return mutate(incident_id, lambda incident: resolve_resource_conflict(incident, request.option_id, request.approver))

    @router.post("/incidents/{incident_id}/escalate")
    def escalate(incident_id: str) -> dict[str, Any]:
        return mutate(incident_id, escalate_nonresponse)

    @router.post("/incidents/{incident_id}/recover")
    def recover(incident_id: str, request: ApprovalRequest) -> dict[str, Any]:
        return mutate(incident_id, lambda incident: rescind_and_recover(incident, request.approver))

    @router.post("/demo/full")
    def full_demo() -> dict[str, Any]:
        incident = run_full_demo()
        store.put(incident)
        return incident

    @router.post("/reset")
    def reset() -> dict[str, Any]:
        store.clear()
        return {"ok": True}

    @router.get("/research")
    def research() -> dict[str, Any]:
        incident = create_incident()
        return {
            "sources": list(incident["sources"].values()),
            "prior_art": {
                "title": "UOMS Boil Water Notice Workflows",
                "url": "https://uoms.canopymapping.co/boil-water-notice-management-software",
                "already_covers": "zone, critical-customer identification, approval, notification, audit, and rescission",
                "our_boundary": "facility-specific response execution, evidence, resource conflict, escalation, and recovery verification",
            },
            "claim_boundary": "The sources support the coordination problem and playbook structure; they do not validate One Advisory or prove improved outcomes.",
        }

    @router.get("/registry")
    def registry() -> dict[str, Any]:
        return {"agents": create_incident()["registry"], "synthetic": True}

    @router.get("/proof")
    def proof() -> dict[str, Any]:
        checks: list[dict[str, Any]] = []

        def check(name: str, passed: bool, detail: str = "") -> None:
            checks.append({"check": name, "pass": bool(passed), "detail": detail})

        incident = create_incident()
        check("system did not issue the advisory", not incident["advisory"]["decision_by_system"])
        try:
            approve_proposals(incident, "Jordan Lee")
            blocked = False
        except ValueError:
            blocked = True
        check("tasks cannot be approved before source-backed proposals", blocked)
        activate_fleet(incident)
        check("all nine proposed tasks retain source IDs", all(task["source_id"] in incident["sources"] for facility in incident["facilities"] for task in facility["tasks"]))
        reject_unregistered_action(incident)
        check("unregistered autonomous closure is rejected", len(incident["policy_rejections"]) == 1)
        approve_proposals(incident, "Jordan Lee — synthetic")
        receive_facility_updates(incident)
        detect_resource_conflict(incident)
        check("resource agent makes no allocation", incident["resource_conflict"]["selected"] is None and not incident["resource_conflict"]["selected_by_ai"])
        try:
            resolve_resource_conflict(incident, "invented", "Jordan Lee")
            invalid_blocked = False
        except ValueError:
            invalid_blocked = True
        check("unsupported allocation is rejected", invalid_blocked)
        resolve_resource_conflict(incident, "slot-to-ltc", "Jordan Lee — synthetic")
        check("resource allocation records named human authority", not incident["resource_conflict"]["selected_by_ai"] and bool(incident["resource_conflict"]["approver"]))
        escalate_nonresponse(incident)
        check("missed acknowledgement creates a routed escalation", len(incident["escalations"]) == 1)
        rescind_and_recover(incident, "Jordan Lee — synthetic")
        check("system did not originate rescission", bool(incident["advisory"]["rescinded_by"]))
        check("recovery closes all three facility loops", len(incident["recovery"]["checks"]) == 3 and incident["status"] == "closed")
        check("timeline sequence is immutable and ordered", [row["sequence"] for row in incident["timeline"]] == list(range(1, len(incident["timeline"]) + 1)))
        return {"passed": sum(row["pass"] for row in checks), "total": len(checks), "checks": checks}

    @router.get("/conformance")
    def conformance() -> dict[str, Any]:
        return {
            "category": "The Fortified Enterprise Fleet",
            "requirements": [
                {"requirement": "agent discovery", "implementation": "versioned registry with scope, approval, and data class", "proof": "/api/registry"},
                {"requirement": "cross-department orchestration", "implementation": "facility roles, policy, resource, escalation, recovery, and audit", "proof": "live incident console"},
                {"requirement": "long-term state", "implementation": "structured facility memory and incident history", "proof": "facility memory records"},
                {"requirement": "security and governance", "implementation": "registered scope, approval gates, policy rejection, minimum synthetic data", "proof": "/api/proof"},
                {"requirement": "observability", "implementation": "ordered actor/action/evidence audit timeline", "proof": "incident timeline"},
            ],
            "limitations": [
                "The advisory, facilities, people, contacts, evidence, resources, and connectors are synthetic.",
                "The system cannot issue or rescind an advisory, close a facility, or allocate scarce resources.",
                "The product begins after an authorized advisory and does not replace utility notification software.",
                "No public-health outcome has been validated.",
            ],
        }

    return router

