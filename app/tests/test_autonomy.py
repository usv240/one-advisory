from pathlib import Path

from fastapi.testclient import TestClient

from service.main import app


client = TestClient(app)


def test_one_request_demo_completes_full_governed_fleet():
    incident = client.post("/api/demo/full").json()
    assert incident["status"] == "closed"
    assert incident["autonomy"]["complete"] is True
    assert incident["resource_conflict"]["selected_by_ai"] is False
    assert len(incident["recovery"]["checks"]) == 3


def test_authorized_feed_auto_activates_and_delivers_standing_playbooks():
    incident = client.post("/api/incidents").json()
    assert incident["status"] == "instructions_delivered"
    assert incident["autonomy"]["last_run_actions"] == [
        "registered_fleet_activated",
        "unauthorized_action_rejected",
        "facility_playbooks_delivered",
    ]
    assert incident["autonomy"]["current_wait"] == "facility_update_events"


def test_facility_events_and_allocation_each_resume_until_next_real_gate():
    incident = client.post("/api/incidents").json()
    incident = client.post(f"/api/incidents/{incident['incident_id']}/facility-updates").json()
    assert incident["status"] == "resource_conflict"
    assert incident["autonomy"]["last_run_actions"] == ["resource_conflict_detected"]

    incident = client.post(
        f"/api/incidents/{incident['incident_id']}/allocate",
        json={"option_id": "slot-to-ltc", "approver": "Jordan Lee - synthetic"},
    ).json()
    assert incident["status"] == "response_verified"
    assert incident["autonomy"]["last_run_actions"] == ["nonresponse_escalated"]
    assert incident["autonomy"]["current_wait"] == "authorized_rescission_event"


def test_autopilot_does_not_invent_missing_facility_or_authority_events():
    incident = client.post("/api/incidents").json()
    resumed = client.post(f"/api/incidents/{incident['incident_id']}/autopilot").json()
    assert resumed["status"] == "instructions_delivered"
    assert resumed["autonomy"]["last_run_actions"] == []

def test_primary_demo_is_one_server_request_with_distinct_receipt():
    web = Path(__file__).resolve().parents[1] / "web"
    html = (web / "index.html").read_text(encoding="utf-8")
    script = (web / "app.js").read_text(encoding="utf-8")
    css = (web / "autonomy.css").read_text(encoding="utf-8")
    assert 'id="autonomy-receipt"' in html and 'aria-live="polite"' in html
    assert "/static/autonomy.css" in html and "Complete synthetic tabletop" in html
    assert 'api("/api/demo/full"' in script
    assert "while (" not in script and "while(" not in script
    assert ".autonomy-command" in css

def test_health_declares_autonomy_mode():
    assert client.get("/health").json()["autonomy"] == "governed-multi-agent-auto-continuation"
