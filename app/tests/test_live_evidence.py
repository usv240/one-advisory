from pathlib import Path
from types import SimpleNamespace

from one_advisory.live_evidence import LiveEvidenceRunner
from one_advisory.workflow import create_incident


class Reader:
    def read(self, artifact, mime):
        return SimpleNamespace(transcription="ACTIVE East zone Jordan Lee", fields=[
            {"key": "status", "value": "active", "quote": "ACTIVE", "confidence": 1},
            {"key": "zone", "value": "East zone", "quote": "East zone", "confidence": 1},
            {"key": "authority", "value": "Jordan Lee", "quote": "Jordan Lee", "confidence": 1},
        ], dropped=[])


class Router:
    def rank(self, query, candidates):
        scores = {key: index / 10 for index, key in enumerate(candidates, 1)}
        return {"model": "gemini-embedding-001", "mode": "live-vertex-ai", "winner": max(scores, key=scores.get), "scores": scores, "live": True}


def test_live_models_route_facility_processing_without_allocating():
    web = Path(__file__).resolve().parents[1] / "web"
    incident = LiveEvidenceRunner("test", web, Reader(), Router()).apply(create_incident())
    assert incident["advisory_extraction"]["mode"] == "live-vertex-ai"
    assert len(incident["semantic_processing_order"]) == 3
    assert incident["resource_conflict"] is None
