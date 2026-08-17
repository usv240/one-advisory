"""Typed public-sandbox routes for custom synthetic One Advisory incidents."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from one_advisory.pilot import create_pilot_incident
from one_advisory.store import IncidentStore
from one_advisory.workflow import public_view


class AdvisoryInput(BaseModel):
    title: str = Field(min_length=4, max_length=180)
    authority: str = Field(min_length=4, max_length=180)
    issued_at: str = Field(min_length=10, max_length=60)
    zone_name: str = Field(min_length=2, max_length=120)
    source_title: str = Field(min_length=3, max_length=180)
    source_url: HttpUrl


class FacilityInput(BaseModel):
    type: Literal["dialysis", "school_childcare", "long_term_care"]
    name: str = Field(min_length=3, max_length=180)
    contact: str = Field(min_length=3, max_length=180)
    capacity_note: str = Field(default="", max_length=240)


class PilotIncidentRequest(BaseModel):
    synthetic_acknowledgement: Literal[True]
    data_class: Literal["synthetic"] = "synthetic"
    advisory: AdvisoryInput
    facilities: list[FacilityInput] = Field(min_length=3, max_length=3)


def _summary(incident: dict[str, Any]) -> dict[str, Any]:
    return {
        "incident_id": incident["incident_id"],
        "status": incident["status"],
        "title": incident["advisory"]["title"],
        "zone": incident["advisory"]["zone"]["name"],
        "origin": incident.get("origin", "sample_fixture"),
        "created_at": incident.get("created_at", incident["advisory"]["issued_at"]),
    }


def build_pilot_router(store: IncidentStore) -> APIRouter:
    router = APIRouter(prefix="/api/pilot", tags=["one-advisory-pilot"])

    @router.get("/incidents")
    def list_incidents() -> dict[str, Any]:
        incidents = store.list_incidents()
        return {"incidents": [_summary(item) for item in incidents], "count": len(incidents)}

    @router.post("/incidents")
    def open_incident(request: PilotIncidentRequest) -> dict[str, Any]:
        try:
            incident = create_pilot_incident(request.model_dump(mode="json"))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        store.put(incident)
        return public_view(incident)

    @router.get("/readiness")
    def readiness() -> dict[str, Any]:
        return {
            "level": "public synthetic operational sandbox",
            "working_now": [
                "custom fictional advisory intake",
                "multiple durable incidents",
                "custom critical-facility roster",
                "human approval and allocation gates",
                "ordered audit timeline and failure recovery",
            ],
            "public_data_policy": "synthetic-only",
            "required_for_operational_use": [
                "organization identity and tenant isolation",
                "authorized advisory and facility-system connectors",
                "contact consent, delivery reconciliation, and operating procedures",
                "tabletop validation with emergency-management and facility operators",
            ],
            "claim": "One Advisory is not represented as an authorized emergency notification system.",
        }

    return router
