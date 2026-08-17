from fastapi.testclient import TestClient

from service.main import app
from test_pilot import payload


client = TestClient(app)


def test_pilot_incident_create_list_and_readiness():
    created = client.post("/api/pilot/incidents", json=payload())
    assert created.status_code == 200
    incident = created.json()
    listing = client.get("/api/pilot/incidents").json()
    assert any(row["incident_id"] == incident["incident_id"] for row in listing["incidents"])
    readiness = client.get("/api/pilot/readiness").json()
    assert readiness["public_data_policy"] == "synthetic-only"
    assert "not represented as an authorized emergency notification system" in readiness["claim"]
    unacknowledged = payload()
    unacknowledged.pop("synthetic_acknowledgement")
    assert client.post("/api/pilot/incidents", json=unacknowledged).status_code == 422
