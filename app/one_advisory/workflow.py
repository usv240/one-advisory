"""Source-bearing, authority-gated critical-facility response fleet."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

BASE_TIME = datetime(2026, 8, 16, 9, 30, tzinfo=timezone.utc)

SOURCES = {
    "cdc_toolkit": {
        "title": "CDC Drinking Water Advisory Communication Toolkit",
        "url": "https://www.cdc.gov/water-emergency/php/dwact/index.html",
        "use": "Facility-specific planning, communication, follow-up, and evaluation.",
        "authority": "U.S. public-health guidance",
    },
    "cdc_dialysis": {
        "title": "CDC Water Use in Dialysis",
        "url": "https://www.cdc.gov/dialysis-safety/hcp/recommendations-resources/water-use-in-dialysis.html",
        "use": "Dialysis water criticality; does not authorize facility closure or transfer.",
        "authority": "U.S. public-health guidance",
    },
    "cdc_alabama": {
        "title": "CDC MMWR: Extended water-system failure in Alabama",
        "url": "https://www.cdc.gov/mmwr/preview/mmwrhtml/mm6006a1.htm",
        "use": "Historical evidence of communication, institutional, alternative-water, and coordination gaps.",
        "authority": "Published investigation",
    },
    "wv_hospitals": {
        "title": "Hospital response to the West Virginia water crisis",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5587347/",
        "use": "Operational dependencies across clinical and support functions.",
        "authority": "Published investigation",
    },
}

AGENT_REGISTRY = [
    {"id": "registry", "version": "1.0.0", "scope": "synthetic facility intersection", "approval": "none", "data_class": "synthetic operational"},
    {"id": "policy", "version": "1.0.0", "scope": "source-backed task selection", "approval": "none", "data_class": "public guidance"},
    {"id": "dialysis", "version": "1.0.0", "scope": "dialysis task proposals", "approval": "incident commander", "data_class": "synthetic facility"},
    {"id": "school", "version": "1.0.0", "scope": "school/childcare task proposals", "approval": "incident commander", "data_class": "synthetic facility"},
    {"id": "long_term_care", "version": "1.0.0", "scope": "long-term-care task proposals", "approval": "incident commander", "data_class": "synthetic facility"},
    {"id": "resource", "version": "1.0.0", "scope": "conflict detection and options", "approval": "incident commander", "data_class": "synthetic operational"},
    {"id": "recovery", "version": "1.0.0", "scope": "post-rescission checks", "approval": "incident commander", "data_class": "synthetic operational"},
    {"id": "audit", "version": "1.0.0", "scope": "read-only evidence ledger", "approval": "none", "data_class": "synthetic audit"},
]

FACILITY_BLUEPRINTS = [
    {
        "facility_id": "fac-dialysis",
        "name": "Harbor Dialysis Center — synthetic",
        "type": "dialysis",
        "coordinates": {"x": 41, "y": 36},
        "contact": "Charge nurse — synthetic",
        "memory": {"alternate_site": "North County Dialysis — synthetic", "last_drill": "2026-05-14", "open_findings": 0},
        "tasks": [
            {"task_id": "dia-verify-water", "title": "Verify treatment-water status with qualified facility lead", "source_id": "cdc_dialysis", "requires_evidence": True},
            {"task_id": "dia-continuity", "title": "Review approved continuity or transfer plan", "source_id": "cdc_toolkit", "requires_evidence": True},
            {"task_id": "dia-patients", "title": "Prepare approved patient communication and transport list", "source_id": "cdc_toolkit", "requires_evidence": True},
        ],
    },
    {
        "facility_id": "fac-school",
        "name": "Riverbend Learning Center — synthetic",
        "type": "school_childcare",
        "coordinates": {"x": 63, "y": 56},
        "contact": "Site director — synthetic",
        "memory": {"enrollment": 126, "mobility_support": 4, "last_drill": "2026-04-03", "open_findings": 1},
        "tasks": [
            {"task_id": "sch-water", "title": "Confirm approved drinking and hygiene water supply", "source_id": "cdc_toolkit", "requires_evidence": True},
            {"task_id": "sch-food", "title": "Hold water-dependent food service pending official direction", "source_id": "cdc_toolkit", "requires_evidence": True},
            {"task_id": "sch-families", "title": "Prepare accessible family notice for official approval", "source_id": "cdc_toolkit", "requires_evidence": True},
        ],
    },
    {
        "facility_id": "fac-ltc",
        "name": "Cedar House Care — synthetic",
        "type": "long_term_care",
        "coordinates": {"x": 72, "y": 29},
        "contact": "Administrator on call — synthetic",
        "memory": {"residents": 84, "high_support_residents": 19, "last_drill": "2026-06-02", "open_findings": 0},
        "tasks": [
            {"task_id": "ltc-clinical", "title": "Review water-dependent resident care with clinical lead", "source_id": "wv_hospitals", "requires_evidence": True},
            {"task_id": "ltc-hygiene", "title": "Activate approved hygiene and environmental-services controls", "source_id": "cdc_toolkit", "requires_evidence": True},
            {"task_id": "ltc-water", "title": "Confirm alternative-water quantity and delivery access", "source_id": "cdc_toolkit", "requires_evidence": True},
        ],
    },
]


def _iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _append(incident: dict[str, Any], actor: str, action: str, detail: str, status: str = "complete", evidence: list[str] | None = None) -> None:
    incident["timeline"].append({
        "sequence": len(incident["timeline"]) + 1,
        "at": _iso(datetime.now(timezone.utc) if incident.get("clock_mode") == "realtime" else BASE_TIME + timedelta(minutes=len(incident["timeline"]) * 5)),
        "actor": actor,
        "action": action,
        "detail": detail,
        "status": status,
        "evidence_ids": evidence or [],
    })


def create_incident() -> dict[str, Any]:
    incident = {
        "incident_id": f"oa-{uuid4().hex}",
        "synthetic": True,
        "origin": "sample_fixture",
        "data_class": "synthetic",
        "clock_mode": "simulated",
        "created_at": _iso(BASE_TIME),
        "status": "authorized_advisory_received",
        "advisory": {
            "type": "boil_water",
            "title": "Boil-water advisory — synthetic tabletop",
            "authority": "Authorized by Jordan Lee, incident commander — synthetic",
            "issued_at": _iso(BASE_TIME),
            "zone": {"name": "East service zone — synthetic", "polygon": [{"x": 25, "y": 20}, {"x": 83, "y": 18}, {"x": 88, "y": 68}, {"x": 32, "y": 74}]},
            "source_id": "synthetic-authorized-advisory",
            "decision_by_system": False,
            "rescinded": False,
        },
        "sources": deepcopy(SOURCES),
        "registry": deepcopy(AGENT_REGISTRY),
        "facilities": deepcopy(FACILITY_BLUEPRINTS),
        "approvals": [],
        "resource_conflict": None,
        "escalations": [],
        "recovery": {"status": "not_started", "checks": []},
        "policy_rejections": [],
        "timeline": [],
        "safety": {
            "system_issued_advisory": False,
            "system_allocated_scarce_resource": False,
            "outbound_connectors": "sandbox",
            "disclosure": "The system proposes and verifies response work. Authorized officials retain public-health and resource-allocation authority.",
        },
    }
    for facility in incident["facilities"]:
        facility["response_state"] = "identified"
        facility["tasks"] = [{**task, "status": "proposed", "evidence": None} for task in facility["tasks"]]
    _append(incident, "Authorized feed", "Advisory received", "An already-authorized synthetic advisory entered the response system.", evidence=["synthetic-authorized-advisory"])
    return incident


def activate_fleet(incident: dict[str, Any]) -> dict[str, Any]:
    if incident["status"] != "authorized_advisory_received":
        raise ValueError("fleet activation requires an authorized advisory")
    incident["status"] = "proposals_ready"
    for facility in incident["facilities"]:
        facility["response_state"] = "proposal_ready"
    _append(incident, "Registry agent", "Three critical facilities identified", "Registry and memory records were loaded for dialysis, school/childcare, and long-term care.", evidence=["cdc_toolkit"])
    _append(incident, "Policy agent", "Facility tasks proposed", "Nine tasks retain source IDs and remain unapproved.", evidence=["cdc_toolkit", "cdc_dialysis", "wv_hospitals"])
    return incident


def reject_unregistered_action(incident: dict[str, Any]) -> dict[str, Any]:
    rejection = {
        "agent": "generic-autopilot",
        "requested_action": "close every affected facility automatically",
        "reason": "unregistered agent and action outside system authority",
        "at": _iso(BASE_TIME + timedelta(minutes=12)),
    }
    incident["policy_rejections"].append(rejection)
    _append(incident, "Policy gateway", "Unauthorized action rejected", rejection["reason"], status="rejected")
    return incident


def approve_proposals(incident: dict[str, Any], approver: str) -> dict[str, Any]:
    if incident["status"] != "proposals_ready":
        raise ValueError("task approval requires source-backed proposals")
    if len(approver.strip()) < 3:
        raise ValueError("named approver is required")
    incident["approvals"].append({"kind": "facility_tasks", "approver": approver.strip(), "at": _iso(BASE_TIME + timedelta(minutes=15))})
    for facility in incident["facilities"]:
        facility["response_state"] = "instructions_delivered"
        for task in facility["tasks"]:
            task["status"] = "delivered"
    incident["status"] = "instructions_delivered"
    _append(incident, "Incident commander", "Nine tasks approved", f"{approver.strip()} approved differentiated sandbox instructions.", evidence=["facility-tasks-approval"])
    _append(incident, "Contact agent", "Instructions delivered", "Sandbox delivery receipts were recorded for all three facilities.", evidence=["sandbox-delivery-receipts"])
    return incident


def receive_facility_updates(incident: dict[str, Any]) -> dict[str, Any]:
    if incident["status"] != "instructions_delivered":
        raise ValueError("facility updates require delivered instructions")
    dialysis, school, ltc = incident["facilities"]
    dialysis["response_state"] = "evidence_received"
    for task in dialysis["tasks"]:
        task["status"] = "evidenced"
        task["evidence"] = "Synthetic charge-nurse acknowledgement and continuity checklist"
    school["response_state"] = "no_response"
    ltc["response_state"] = "assistance_requested"
    for task in ltc["tasks"][:2]:
        task["status"] = "acknowledged"
    incident["status"] = "responses_in_progress"
    _append(incident, "Dialysis facility", "Response evidence received", "Three approved tasks have synthetic acknowledgement and evidence.", evidence=["dialysis-response-evidence"])
    _append(incident, "Long-term-care facility", "Assistance requested", "The facility reported insufficient alternative water and requested a delivery slot.", status="attention", evidence=["ltc-resource-request"])
    return incident


def detect_resource_conflict(incident: dict[str, Any]) -> dict[str, Any]:
    if incident["status"] != "responses_in_progress":
        raise ValueError("resource analysis requires facility responses")
    incident["resource_conflict"] = {
        "status": "awaiting_human_allocation",
        "resource": "one synthetic emergency-water delivery slot",
        "requests": [
            {"facility_id": "fac-dialysis", "reason": "continuity reserve requested", "source": "dialysis-response-evidence"},
            {"facility_id": "fac-ltc", "reason": "alternative-water shortfall reported", "source": "ltc-resource-request"},
        ],
        "options": [
            {"id": "slot-to-ltc", "description": "Assign the current slot to long-term care; confirm dialysis reserve and alternate site."},
            {"id": "slot-to-dialysis", "description": "Assign the current slot to dialysis; seek a second provider for long-term care."},
            {"id": "hold-for-command", "description": "Hold both requests pending updated operational evidence."},
        ],
        "selected": None,
        "selected_by_ai": False,
    }
    incident["status"] = "resource_conflict"
    _append(incident, "Resource agent", "Scarce-resource conflict surfaced", "Two source-bearing requests compete for one slot; the fleet proposed options but made no allocation.", status="waiting", evidence=["dialysis-response-evidence", "ltc-resource-request"])
    return incident


def resolve_resource_conflict(incident: dict[str, Any], option_id: str, approver: str) -> dict[str, Any]:
    conflict = incident.get("resource_conflict") or {}
    if conflict.get("status") != "awaiting_human_allocation":
        raise ValueError("an unresolved resource conflict is required")
    allowed = {row["id"] for row in conflict["options"]}
    if option_id not in allowed or len(approver.strip()) < 3:
        raise ValueError("supported option and named approver are required")
    conflict["status"] = "allocated_by_human"
    conflict["selected"] = option_id
    conflict["approver"] = approver.strip()
    conflict["selected_by_ai"] = False
    incident["approvals"].append({"kind": "resource_allocation", "approver": approver.strip(), "option": option_id, "at": _iso(BASE_TIME + timedelta(minutes=35))})
    incident["status"] = "allocation_approved"
    _append(incident, "Incident commander", "Resource option selected", f"{approver.strip()} selected {option_id}; the system did not allocate the resource.", evidence=["resource-allocation-approval"])
    return incident


def escalate_nonresponse(incident: dict[str, Any]) -> dict[str, Any]:
    if incident["status"] != "allocation_approved":
        raise ValueError("non-response escalation follows approved resource resolution in this demo")
    school = next(row for row in incident["facilities"] if row["facility_id"] == "fac-school")
    if school["response_state"] != "no_response":
        raise ValueError("no unresolved facility non-response")
    escalation = {"facility_id": school["facility_id"], "reason": "acknowledgement deadline missed", "route": "synthetic duty officer", "status": "delivered"}
    incident["escalations"].append(escalation)
    school["response_state"] = "escalated"
    incident["status"] = "response_verified"
    _append(incident, "Escalation agent", "Missed acknowledgement escalated", "The school/childcare non-response was routed to the synthetic duty officer.", status="attention", evidence=["acknowledgement-deadline", "sandbox-escalation-receipt"])
    return incident


def rescind_and_recover(incident: dict[str, Any], approver: str) -> dict[str, Any]:
    if incident["status"] != "response_verified":
        raise ValueError("recovery requires the active response stage to complete")
    if len(approver.strip()) < 3:
        raise ValueError("named rescission authority is required")
    incident["advisory"]["rescinded"] = True
    incident["advisory"]["rescinded_by"] = approver.strip()
    incident["recovery"] = {
        "status": "complete",
        "checks": [
            {"facility_id": row["facility_id"], "status": "reviewed", "detail": "Synthetic facility-specific recovery checklist completed"}
            for row in incident["facilities"]
        ],
    }
    for facility in incident["facilities"]:
        facility["response_state"] = "recovery_reviewed"
    incident["status"] = "closed"
    _append(incident, "Authorized feed", "Rescission received", f"{approver.strip()} authorized the synthetic rescission; the system did not issue it.", evidence=["synthetic-rescission"])
    _append(incident, "Recovery agent", "Three recovery reviews completed", "Facility-specific recovery checks and the after-action record were completed.", evidence=["recovery-checks", "audit-record"])
    return incident


def advance_safe_automation(incident: dict[str, Any]) -> list[str]:
    """Run governed fleet work until an external event or authority decision is required."""
    actions: list[str] = []
    while True:
        if incident["status"] == "authorized_advisory_received":
            activate_fleet(incident)
            actions.append("registered_fleet_activated")
            reject_unregistered_action(incident)
            actions.append("unauthorized_action_rejected")
            approve_proposals(incident, "Standing response policy - synthetic pre-authorization")
            actions.append("facility_playbooks_delivered")
            continue
        if incident["status"] == "responses_in_progress":
            detect_resource_conflict(incident)
            actions.append("resource_conflict_detected")
            continue
        if incident["status"] == "allocation_approved":
            escalate_nonresponse(incident)
            actions.append("nonresponse_escalated")
            continue
        break
    incident["last_autonomy_run"] = {
        "actions": actions,
        "stopped_at": incident["status"],
        "waiting_for": {
            "instructions_delivered": "facility_update_events",
            "resource_conflict": "incident_commander_allocation",
            "response_verified": "authorized_rescission_event",
            "closed": None,
        }.get(incident["status"], "unsupported_state"),
    }
    return actions

def public_view(incident: dict[str, Any]) -> dict[str, Any]:
    view = deepcopy(incident)
    states = [facility["response_state"] for facility in incident["facilities"]]
    view["metrics"] = {
        "affected_facilities": len(incident["facilities"]),
        "source_backed_tasks": sum(len(row["tasks"]) for row in incident["facilities"]),
        "verified_or_recovery": sum(state in {"evidence_received", "recovery_reviewed"} for state in states),
        "open_escalations": sum(row["status"] != "resolved" for row in incident["escalations"]),
        "policy_rejections": len(incident["policy_rejections"]),
        "human_allocation": bool((incident.get("resource_conflict") or {}).get("selected")),
    }
    view["autonomy"] = {
        "trigger": "authorized advisory feed",
        "automatic_actions": ["activate registered fleet", "apply standing playbooks", "deliver differentiated tasks", "detect resource conflicts", "escalate silence", "run recovery checks"],
        "authority_checkpoints": ["scarce-resource allocation"],
        "external_authority_events": ["advisory issuance", "advisory rescission"],
        "current_wait": None if incident["status"] == "closed" else (incident.get("last_autonomy_run") or {}).get("waiting_for", "authorized_advisory_event"),
        "last_run_actions": (incident.get("last_autonomy_run") or {}).get("actions", []),
        "complete": incident["status"] == "closed",
    }
    return view


def run_full_demo() -> dict[str, Any]:
    incident = create_incident()
    activate_fleet(incident)
    reject_unregistered_action(incident)
    approve_proposals(incident, "Jordan Lee, incident commander — synthetic")
    receive_facility_updates(incident)
    detect_resource_conflict(incident)
    resolve_resource_conflict(incident, "slot-to-ltc", "Jordan Lee, incident commander — synthetic")
    escalate_nonresponse(incident)
    rescind_and_recover(incident, "Jordan Lee, incident commander — synthetic")
    return public_view(incident)



