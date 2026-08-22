"""Fail-closed bridge from the primary workflow to managed Agent Runtime roles."""
from __future__ import annotations

from time import perf_counter
from typing import Any, Callable

from one_advisory.managed_platform import RUNTIME_IDS


class ManagedAgentRejected(RuntimeError):
    pass


class ManagedOrchestrator:
    def __init__(self, project: str, location: str = "us-central1", query: Callable | None = None, attempts: int = 2):
        self.project = project
        self.location = location
        self._query = query
        self.attempts = attempts

    def _remote_query(self, role: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self._query is not None:
            return self._query(role, payload)
        import vertexai

        client = vertexai.Client(project=self.project, location=self.location)
        name = f"projects/{self.project}/locations/{self.location}/reasoningEngines/{RUNTIME_IDS[role]}"
        return client.agent_engines.get(name=name).query(payload=payload)

    def require(self, incident: dict[str, Any], role: str, command: str) -> dict[str, Any]:
        started = perf_counter()
        last_error: Exception | None = None
        for attempt in range(1, self.attempts + 1):
            try:
                result = self._remote_query(role, {
                    "incident_id": incident["incident_id"],
                    "status": incident["status"],
                    "expected_command": command,
                })
                if result.get("agent_role") != role or result.get("proposed_command") != command or not result.get("allowed"):
                    raise ManagedAgentRejected(f"{role} did not authorize its registered command")
                receipt = {
                    "sequence": len(incident.setdefault("managed_agent_trace", [])) + 1,
                    "role": role,
                    "runtime_id": RUNTIME_IDS[role],
                    "command": command,
                    "status_observed": incident["status"],
                    "attempt": attempt,
                    "latency_ms": round((perf_counter() - started) * 1000),
                    "result": "accepted",
                }
                incident["managed_agent_trace"].append(receipt)
                return receipt
            except Exception as exc:
                last_error = exc
        raise ManagedAgentRejected(f"managed runtime unavailable or rejected {role}/{command}") from last_error
