from fastapi.testclient import TestClient

from service.main import app


def test_public_trace_is_useful_and_redacted():
    client = TestClient(app)
    incident = client.post("/api/demo/full").json()
    trace = client.get(f'/api/incidents/{incident["incident_id"]}/trace').json()
    assert trace["event_count"] == len(incident["timeline"])
    serialized = str(trace).lower()
    assert "raw prompts" in serialized
    assert "requests" not in serialized and "approver" not in serialized
