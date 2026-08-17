from fastapi.testclient import TestClient

from service.main import app
from test_pilot import payload


client = TestClient(app)


def post(path, body=None):
    return client.post(path, json=body or {})


def test_custom_synthetic_incident_completes_without_losing_supplied_facts():
    incident = post("/api/pilot/incidents", payload()).json()
    incident_id = incident["incident_id"]
    post(f"/api/incidents/{incident_id}/activate")
    post(f"/api/incidents/{incident_id}/policy-test")
    post(f"/api/incidents/{incident_id}/approve", {"approver": "Exercise commander - fictional"})
    post(f"/api/incidents/{incident_id}/facility-updates")
    post(f"/api/incidents/{incident_id}/detect-conflict")
    post(
        f"/api/incidents/{incident_id}/allocate",
        {"option_id": "slot-to-ltc", "approver": "Exercise commander - fictional"},
    )
    post(f"/api/incidents/{incident_id}/escalate")
    closed = post(
        f"/api/incidents/{incident_id}/recover",
        {"approver": "Exercise commander - fictional"},
    ).json()
    assert closed["status"] == "closed"
    assert closed["advisory"]["title"] == "North zone boil-water exercise"
    assert closed["facilities"][0]["name"] == "North Dialysis - fictional"
    assert closed["resource_conflict"]["selected_by_ai"] is False
    assert post("/api/reset").status_code == 403
