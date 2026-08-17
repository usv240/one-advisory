"""Input-driven synthetic incident intake for the public hackathon sandbox."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from one_advisory.workflow import FACILITY_BLUEPRINTS, SOURCES, _append, create_incident


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def create_pilot_incident(intake: dict[str, Any]) -> dict[str, Any]:
    """Create a fictional incident from supplied advisory and facility facts."""

    if intake.get("data_class") != "synthetic":
        raise ValueError("the public sandbox accepts synthetic data only")
    facilities = intake.get("facilities") or []
    expected = ["dialysis", "school_childcare", "long_term_care"]
    if [row.get("type") for row in facilities] != expected:
        raise ValueError("provide one dialysis, school/childcare, and long-term-care facility in order")

    incident = create_incident()
    incident.update(
        {
            "origin": "pilot_input",
            "data_class": "synthetic",
            "clock_mode": "realtime",
            "created_at": _iso_now(),
        }
    )
    advisory = intake["advisory"]
    incident["advisory"].update(
        {
            "title": advisory["title"].strip(),
            "authority": advisory["authority"].strip(),
            "issued_at": advisory["issued_at"],
            "zone": {
                "name": advisory["zone_name"].strip(),
                "polygon": deepcopy(incident["advisory"]["zone"]["polygon"]),
            },
            "source_id": "user-supplied-synthetic-advisory",
        }
    )
    incident["sources"] = deepcopy(SOURCES)
    incident["sources"]["pilot_advisory"] = {
        "title": advisory["source_title"].strip(),
        "url": str(advisory["source_url"]),
        "use": "User-supplied source for this fictional advisory exercise.",
        "authority": "Synthetic exercise input; not independently verified by One Advisory",
    }
    for blueprint, supplied in zip(FACILITY_BLUEPRINTS, facilities, strict=True):
        facility = next(row for row in incident["facilities"] if row["type"] == blueprint["type"])
        facility["name"] = supplied["name"].strip()
        facility["contact"] = supplied["contact"].strip()
        facility["memory"]["capacity_note"] = supplied.get("capacity_note", "").strip()

    incident["timeline"] = []
    _append(
        incident,
        "Authorized synthetic intake",
        "Advisory exercise created",
        f"{incident['advisory']['title']} was supplied for {incident['advisory']['zone']['name']}; One Advisory did not issue it.",
        evidence=["user-supplied-synthetic-advisory", "pilot_advisory"],
    )
    return incident
