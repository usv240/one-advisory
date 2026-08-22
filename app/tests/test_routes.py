from fastapi.testclient import TestClient

from service.main import app

client = TestClient(app)


def post(path, body=None):
    return client.post(path, json=body or {})


def test_public_contract_and_full_flow():
    assert client.get("/").status_code == 200
    health = client.get("/health").json()
    assert health["advisory_authority"] == health["resource_authority"] == "human-only"
    incident = post("/api/incidents").json()
    incident_id = incident["incident_id"]
    assert incident["status"] == "instructions_delivered"
    incident = post(f"/api/incidents/{incident_id}/facility-updates").json()
    assert incident["status"] == "resource_conflict"
    assert incident["resource_conflict"]["selected"] is None
    incident = post(f"/api/incidents/{incident_id}/allocate", {"option_id": "slot-to-ltc", "approver": "Jordan Lee - synthetic"}).json()
    assert incident["status"] == "response_verified"
    incident = post(f"/api/incidents/{incident_id}/recover", {"approver": "Jordan Lee - synthetic"}).json()
    assert incident["status"] == "closed"


def test_proof_research_registry_and_conformance():
    proof = client.get("/api/proof").json()
    assert proof["passed"] == proof["total"] == 11
    research = client.get("/api/research").json()
    assert "do not validate One Advisory" in research["claim_boundary"]
    assert "facility-specific" in research["prior_art"]["our_boundary"]
    assert len(client.get("/api/registry").json()["agents"]) == 8
    assert client.get("/api/conformance").json()["category"] == "The Fortified Enterprise Fleet"


def test_no_endpoint_can_issue_close_or_auto_allocate():
    paths = " ".join(app.openapi()["paths"])
    for forbidden in ["/issue", "/close-facility", "/auto-allocate", "/evacuate"]:
        assert forbidden not in paths
