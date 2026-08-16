from fastapi.testclient import TestClient

from one_advisory.failures import choose_contact_recovery, report_contact_failure, report_source_unavailable, restore_source
from one_advisory.workflow import activate_fleet, approve_proposals, create_incident
from service.main import app


client = TestClient(app)


def test_source_failure_is_fail_closed_and_recoverable():
    incident = create_incident(); activate_fleet(incident); report_source_unavailable(incident)
    assert incident["status"] == "evidence_blocked"
    assert incident["evidence_gate"]["system_authorization"] is None
    assert any(task["status"] == "blocked_missing_source" for facility in incident["facilities"] for task in facility["tasks"])
    restore_source(incident)
    assert incident["status"] == "proposals_ready"


def test_contact_failure_never_invents_delivery_or_route():
    incident = create_incident(); activate_fleet(incident); approve_proposals(incident, "Jordan Lee - synthetic")
    report_contact_failure(incident)
    school = next(row for row in incident["facilities"] if row["facility_id"] == "fac-school")
    assert school["response_state"] == "delivery_failed"
    assert school["contact_recovery"]["selected"] is None
    choose_contact_recovery(incident, "Jordan Lee - synthetic")
    assert school["contact_recovery"]["selected_by_ai"] is False


def test_hardening_proof_and_trace_headers():
    proof = client.get("/api/hardening/proof").json()
    assert proof["passed"] == proof["total"] == 8
    health = client.get("/health")
    assert health.headers["x-agent-trace-id"]


def test_three_facility_wakes_fire_once():
    incident_id = client.post("/api/incidents").json()["incident_id"]
    assert client.post(f"/api/incidents/{incident_id}/activate").status_code == 200
    assert client.post(f"/api/hardening/incidents/{incident_id}/approve-and-watch", json={"approver": "Jordan Lee - synthetic"}).status_code == 200
    wakes = client.get(f"/api/hardening/incidents/{incident_id}/wakes").json()["wakes"]
    assert len(wakes) == 3
    client.post("/api/hardening/advance", json={"minutes": 21})
    assert all(row["status"] == "done" for row in client.get(f"/api/hardening/incidents/{incident_id}/wakes").json()["wakes"])

