"""Fail-closed incident paths for the One Advisory tabletop."""

from __future__ import annotations

from one_advisory.workflow import _append


def report_source_unavailable(incident):
    if incident["status"] != "proposals_ready":
        raise ValueError("source loss can only block unapproved proposals")
    incident["status"] = "evidence_blocked"
    incident["evidence_gate"] = {
        "missing_source": "cdc_toolkit",
        "unsupported_tasks_removed": True,
        "system_authorization": None,
    }
    for facility in incident["facilities"]:
        for task in facility["tasks"]:
            if task["source_id"] == "cdc_toolkit":
                task["status"] = "blocked_missing_source"
    _append(incident, "Evidence gateway", "Unavailable source stopped approval", "Unsupported tasks were blocked, not guessed.", status="blocked")
    return incident


def restore_source(incident):
    if incident["status"] != "evidence_blocked":
        raise ValueError("no blocked source to restore")
    for facility in incident["facilities"]:
        for task in facility["tasks"]:
            if task["status"] == "blocked_missing_source":
                task["status"] = "proposed"
    incident["evidence_gate"]["restored"] = True
    incident["status"] = "proposals_ready"
    _append(incident, "Evidence gateway", "Source restored", "Original source-bearing proposals are ready for human approval.")
    return incident


def report_contact_failure(incident, facility_id="fac-school"):
    if incident["status"] != "instructions_delivered":
        raise ValueError("contact recovery requires approved delivered instructions")
    facility = next((row for row in incident["facilities"] if row["facility_id"] == facility_id), None)
    if facility is None:
        raise ValueError("unknown facility")
    facility["response_state"] = "delivery_failed"
    facility["contact_recovery"] = {
        "status": "human_choice_required",
        "options": ["synthetic duty officer", "verified alternate number"],
        "selected": None,
        "selected_by_ai": False,
        "external_contact_sent": False,
    }
    incident["status"] = "contact_failure"
    _append(incident, "Contact agent", "Delivery failure surfaced", "No acknowledgement was inferred and no alternate route was selected.", status="attention")
    return incident


def choose_contact_recovery(incident, chosen_by, facility_id="fac-school"):
    if incident["status"] != "contact_failure" or len(chosen_by.strip()) < 3:
        raise ValueError("a named human must select contact recovery")
    facility = next(row for row in incident["facilities"] if row["facility_id"] == facility_id)
    recovery = facility["contact_recovery"]
    recovery.update({"status": "prepared_sandbox", "selected": "synthetic duty officer", "selected_by": chosen_by.strip()})
    incident["status"] = "instructions_delivered"
    _append(incident, chosen_by.strip(), "Alternate contact route selected", "A sandbox route was prepared; delivery remains unconfirmed.")
    return incident


def report_rescission_ambiguity(incident):
    if incident["status"] != "response_verified":
        raise ValueError("rescission validation requires completed active response")
    incident["status"] = "rescission_blocked"
    incident["rescission_gate"] = {"authority_verified": False, "system_rescinded": False, "recovery_started": False}
    _append(incident, "Authority gateway", "Ambiguous rescission rejected", "Active controls remain in place until a named authority is verified.", status="blocked")
    return incident

