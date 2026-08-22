import pytest

from one_advisory.managed_orchestrator import ManagedAgentRejected, ManagedOrchestrator
from one_advisory.workflow import create_incident, run_full_demo


def command_query(role, payload):
    return {"agent_role": role, "proposed_command": payload["expected_command"], "allowed": True}


def test_full_workflow_is_gated_by_all_managed_roles():
    orchestrator = ManagedOrchestrator("test", query=command_query)
    result = run_full_demo(create_incident(), orchestrator)
    receipts = result["managed_agent_trace"]
    assert result["status"] == "closed"
    assert {row["role"] for row in receipts} == {
        "facility-fleet", "policy-gateway", "resource-coordinator", "recovery-verifier"
    }
    assert len(receipts) == 6


def test_managed_rejection_fails_closed_after_bounded_retry():
    calls = []
    def reject(role, payload):
        calls.append((role, payload))
        return {"agent_role": role, "proposed_command": None, "allowed": False}
    orchestrator = ManagedOrchestrator("test", query=reject, attempts=2)
    with pytest.raises(ManagedAgentRejected):
        orchestrator.require(create_incident(), "facility-fleet", "activate_fleet")
    assert len(calls) == 2
