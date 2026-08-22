from fastapi import FastAPI
from fastapi.testclient import TestClient

from one_advisory.store import MemoryIncidentStore
from service.routes import build_router


class Recorder:
    def __init__(self):
        self.calls = []

    def require(self, incident, role, command):
        self.calls.append((incident["status"], role, command))


def test_public_auto_route_cannot_bypass_managed_command_gates():
    recorder = Recorder()
    app = FastAPI()
    app.include_router(build_router(MemoryIncidentStore(), managed_orchestrator=recorder))
    response = TestClient(app).post("/api/incidents")
    assert response.status_code == 200
    assert [row[2] for row in recorder.calls] == [
        "activate_fleet", "reject_unregistered_action", "deliver_standing_playbook"
    ]
