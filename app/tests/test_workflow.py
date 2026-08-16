import pytest

from one_advisory.workflow import (
    activate_fleet,
    approve_proposals,
    create_incident,
    detect_resource_conflict,
    escalate_nonresponse,
    receive_facility_updates,
    reject_unregistered_action,
    rescind_and_recover,
    resolve_resource_conflict,
    run_full_demo,
)


def test_incident_starts_from_authorized_human_advisory():
    incident = create_incident()
    assert incident["status"] == "authorized_advisory_received"
    assert incident["advisory"]["decision_by_system"] is False
    assert len(incident["facilities"]) == 3


def test_task_proposals_are_source_backed_and_unapproved():
    incident = create_incident()
    activate_fleet(incident)
    tasks = [task for facility in incident["facilities"] for task in facility["tasks"]]
    assert len(tasks) == 9
    assert all(task["status"] == "proposed" for task in tasks)
    assert all(task["source_id"] in incident["sources"] for task in tasks)


def test_approval_before_proposal_is_blocked():
    with pytest.raises(ValueError):
        approve_proposals(create_incident(), "Jordan Lee")


def test_policy_gateway_records_rejection():
    incident = create_incident()
    activate_fleet(incident)
    reject_unregistered_action(incident)
    assert incident["policy_rejections"][0]["agent"] == "generic-autopilot"


def test_resource_agent_surfaces_but_does_not_resolve_conflict():
    incident = create_incident()
    activate_fleet(incident)
    approve_proposals(incident, "Jordan Lee")
    receive_facility_updates(incident)
    detect_resource_conflict(incident)
    assert incident["resource_conflict"]["selected"] is None
    assert incident["resource_conflict"]["selected_by_ai"] is False


@pytest.mark.parametrize("option", ["invented", "auto", "split", ""])
def test_unsupported_resource_options_are_blocked(option):
    incident = create_incident()
    activate_fleet(incident)
    approve_proposals(incident, "Jordan Lee")
    receive_facility_updates(incident)
    detect_resource_conflict(incident)
    with pytest.raises(ValueError):
        resolve_resource_conflict(incident, option, "Jordan Lee")


def test_full_flow_has_human_allocation_escalation_and_recovery():
    incident = run_full_demo()
    assert incident["status"] == "closed"
    assert incident["resource_conflict"]["selected"] == "slot-to-ltc"
    assert incident["resource_conflict"]["selected_by_ai"] is False
    assert len(incident["escalations"]) == 1
    assert len(incident["recovery"]["checks"]) == 3


def test_recovery_cannot_run_early():
    with pytest.raises(ValueError):
        rescind_and_recover(create_incident(), "Jordan Lee")

