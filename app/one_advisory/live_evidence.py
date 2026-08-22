"""Live, fail-closed model evidence for the public synthetic advisory workflow."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from time import perf_counter
from typing import Any

from one_advisory.reader import AdvisoryReader, VertexAdvisoryClient
from spine.semantic_routing import VertexSemanticRouter


class LiveEvidenceRunner:
    def __init__(self, project: str, web_root: Path, reader=None, router=None):
        self.reader = reader or AdvisoryReader(VertexAdvisoryClient(project))
        self.router = router or VertexSemanticRouter(project)
        self.fixture = web_root / "advisory-fixture.png"

    def apply(self, incident: dict[str, Any]) -> dict[str, Any]:
        artifact = self.fixture.read_bytes()
        started = perf_counter()
        result = self.reader.read(artifact, "image/png")
        if len(result.fields) < 3:
            raise RuntimeError("live advisory extraction retained fewer than three verified fields")
        by_key = {row["key"]: row["value"] for row in result.fields}
        if "authority" in by_key:
            incident["advisory"]["authority"] = by_key["authority"]
        route = self.router.rank(
            result.transcription,
            {
                row["facility_id"]: " ".join([row["type"], row["name"], *(task["title"] for task in row["tasks"])])
                for row in incident["facilities"]
            },
        )
        for row in incident["facilities"]:
            row["semantic_priority"] = route["scores"][row["facility_id"]]
        incident["semantic_processing_order"] = [row["facility_id"] for row in sorted(incident["facilities"], key=lambda row: row["semantic_priority"], reverse=True)]
        incident["advisory_extraction"] = {
            "model": "gemini-3.5-flash",
            "mode": "live-vertex-ai",
            "transcription": result.transcription,
            "fields": result.fields,
            "accuracy": {"matched": len(result.fields), "total": len(result.fields) + len(result.dropped), "invented": 0},
        }
        incident["model_execution"] = {
            "live": True,
            "model": "gemini-3.5-flash",
            "artifact_sha256": sha256(artifact).hexdigest(),
            "verified_fields": len(result.fields),
            "dropped_fields": len(result.dropped),
            "latency_ms": round((perf_counter() - started) * 1000),
        }
        incident["semantic_routing"] = route
        incident["timeline"].append({
            "sequence": len(incident["timeline"]) + 1,
            "at": incident["created_at"],
            "actor": "Live intake agent",
            "action": "Authorized advisory verified and routed",
            "detail": "Gemini retained exact-quoted fields; embeddings prioritized playbook processing without issuing policy or allocating resources.",
            "status": "complete",
            "evidence_ids": ["synthetic-authorized-advisory", route["winner"]],
        })
        return incident
