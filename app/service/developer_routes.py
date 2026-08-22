"""Stable authenticated API for One Advisory integrations."""
from __future__ import annotations
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException

from one_advisory.pilot import create_pilot_incident
from one_advisory.store import IncidentStore
from one_advisory.workflow import advance_safe_automation, create_incident, public_view, receive_facility_updates, rescind_and_recover, resolve_resource_conflict, run_full_demo
from service.pilot_routes import PilotIncidentRequest
from service.routes import AllocationRequest, ApprovalRequest
from spine.developer_access import DeveloperAccessManager, api_key_guard
from spine.public_trace import public_action_trace


def build_developer_router(store: IncidentStore, access: DeveloperAccessManager, scheduler=None, *, model_runner=None, managed_orchestrator=None) -> APIRouter:
    router = APIRouter(prefix="/v1", tags=["One Advisory v1"], dependencies=[Depends(api_key_guard(access))])

    def require(incident_id: str) -> dict[str, Any]:
        incident = store.get(incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail=f"no incident {incident_id}")
        return incident

    def save(incident: dict[str, Any]) -> dict[str, Any]:
        store.put(incident)
        return public_view(incident)

    @router.post("/incidents", status_code=201)
    def create(payload: PilotIncidentRequest) -> dict[str, Any]:
        try:
            incident = create_pilot_incident(payload.model_dump(mode="json"))
            advance_safe_automation(incident, managed_orchestrator)
            if scheduler is not None and incident["status"] == "instructions_delivered":
                for facility in incident["facilities"]:
                    scheduler.sleep_for(incident["incident_id"], "facility_ack_check", timedelta(minutes=20), {"facility_id": facility["facility_id"]}, facility["facility_id"])
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return save(incident)

    @router.get("/incidents/{incident_id}")
    def read(incident_id: str) -> dict[str, Any]:
        return public_view(require(incident_id))

    @router.post("/incidents/{incident_id}/facility-update-events")
    def facility_updates(incident_id: str) -> dict[str, Any]:
        incident = require(incident_id)
        try:
            receive_facility_updates(incident)
            advance_safe_automation(incident, managed_orchestrator)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return save(incident)

    @router.post("/incidents/{incident_id}/allocation-decisions")
    def allocation(incident_id: str, payload: AllocationRequest) -> dict[str, Any]:
        incident = require(incident_id)
        try:
            resolve_resource_conflict(incident, payload.option_id, payload.approver)
            advance_safe_automation(incident, managed_orchestrator)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return save(incident)

    @router.post("/incidents/{incident_id}/rescission-events")
    def rescission(incident_id: str, payload: ApprovalRequest) -> dict[str, Any]:
        incident = require(incident_id)
        try:
            if managed_orchestrator is not None:
                managed_orchestrator.require(incident, "recovery-verifier", "verify_recovery")
            rescind_and_recover(incident, payload.approver)
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return save(incident)

    @router.get("/incidents/{incident_id}/trace")
    def trace(incident_id: str) -> dict[str, Any]:
        return public_action_trace(require(incident_id), "incident_id")

    @router.get("/incidents/{incident_id}/autonomy-proof")
    def autonomy(incident_id: str) -> dict[str, Any]:
        return public_view(require(incident_id))["autonomy_proof"]

    @router.post("/tabletop-runs", status_code=201)
    def tabletop() -> dict[str, Any]:
        incident = create_incident()
        if model_runner is not None:
            try:
                model_runner.apply(incident)
            except Exception as exc:
                raise HTTPException(status_code=503, detail="live Gemini evidence unavailable; no replay substituted") from exc
        result = run_full_demo(incident, managed_orchestrator)
        store.put(incident)
        return result

    return router
