"""Managed Agent Runtime adapter for four bounded read-only capabilities."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BACKEND_URL = os.getenv(
    "ONE_ADVISORY_BACKEND_URL",
    "https://one-advisory-109051079423.us-central1.run.app",
).rstrip("/")
ROLE = os.getenv("ONE_ADVISORY_AGENT_ROLE", "facility-fleet")


class GuardrailRejected(ValueError):
    pass


class CapabilityInvocationError(RuntimeError):
    pass


class StructuralGuard:
    """Bound payload size/type and reject instruction-shaped control text."""

    MAX_REQUEST_BYTES = 4096
    MAX_RESPONSE_BYTES = 1_000_000
    CONTROL_PHRASES = (
        "ignore previous",
        "system prompt",
        "developer message",
        "override policy",
    )

    @classmethod
    def screen_request(cls, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise GuardrailRejected("request must be an object")
        serialized = json.dumps(payload, sort_keys=True)
        if len(serialized.encode("utf-8")) > cls.MAX_REQUEST_BYTES:
            raise GuardrailRejected("request exceeds bounded size")
        lowered = serialized.lower()
        if any(phrase in lowered for phrase in cls.CONTROL_PHRASES):
            raise GuardrailRejected("instruction-shaped request rejected")
        return {
            "screened": True,
            "control": "local-structural-boundary",
            "bytes": len(serialized.encode("utf-8")),
        }

    @classmethod
    def screen_response(cls, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise GuardrailRejected("upstream response must be an object")
        size = len(json.dumps(payload, sort_keys=True).encode("utf-8"))
        if size > cls.MAX_RESPONSE_BYTES:
            raise GuardrailRejected("upstream response exceeds bounded size")
        return {
            "screened": True,
            "control": "local-structural-boundary",
            "bytes": size,
        }


@dataclass(frozen=True)
class Capability:
    method: str
    path: str


CAPABILITIES = {
    "facility-fleet": Capability("GET", "/api/registry"),
    "policy-gateway": Capability("GET", "/api/proof"),
    "resource-coordinator": Capability("GET", "/api/conformance"),
    "recovery-verifier": Capability("GET", "/api/hardening/proof"),
}


class OneAdvisoryRuntimeAgent:
    def __init__(
        self,
        role: str = ROLE,
        backend_url: str = BACKEND_URL,
        armor: Any | None = None,
        opener: Callable[..., Any] = urlopen,
    ):
        if role not in CAPABILITIES:
            raise ValueError(f"unsupported role: {role}")
        self.role = role
        self.backend_url = backend_url
        self.armor = armor or StructuralGuard()
        self._opener = opener

    def query(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = payload or {}
        request_guardrail = self.armor.screen_request(body)
        capability = CAPABILITIES[self.role]
        request = Request(
            self.backend_url + capability.path,
            method=capability.method,
        )
        try:
            with self._opener(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise CapabilityInvocationError(
                f"{self.role} invocation failed: {type(exc).__name__}"
            ) from exc
        response_guardrail = self.armor.screen_response(result)
        return {
            "agent_role": self.role,
            "invoked": capability.path,
            "result": result,
            "guardrails": {
                "request": request_guardrail,
                "response": response_guardrail,
            },
            "managed_security_boundary": {
                "gateway": "day-three-ingress",
                "model_armor_templates": [
                    "one-advisory-agent-input",
                    "one-advisory-agent-output",
                ],
                "inline_model_armor_claimed": False,
            },
        }


root_agent = OneAdvisoryRuntimeAgent()
