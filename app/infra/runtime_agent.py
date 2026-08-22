"""Managed Agent Runtime adapter for bounded operational command proposals."""
from __future__ import annotations

import json
import os
from typing import Any

ROLE = os.getenv("ONE_ADVISORY_AGENT_ROLE", "facility-fleet")


class GuardrailRejected(ValueError):
    pass


class StructuralGuard:
    MAX_REQUEST_BYTES = 4096
    CONTROL_PHRASES = ("ignore previous", "system prompt", "developer message", "override policy")

    @classmethod
    def screen_request(cls, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise GuardrailRejected("request must be an object")
        serialized = json.dumps(payload, sort_keys=True)
        if len(serialized.encode()) > cls.MAX_REQUEST_BYTES:
            raise GuardrailRejected("request exceeds bounded size")
        if any(phrase in serialized.lower() for phrase in cls.CONTROL_PHRASES):
            raise GuardrailRejected("instruction-shaped request rejected")
        return {"screened": True, "control": "local-structural-boundary", "bytes": len(serialized.encode())}


COMMAND_STATES = {
    "facility-fleet": {"activate_fleet": {"authorized_advisory_received"}},
    "policy-gateway": {
        "reject_unregistered_action": {"proposals_ready"},
        "deliver_standing_playbook": {"proposals_ready"},
    },
    "resource-coordinator": {
        "detect_resource_conflict": {"responses_in_progress"},
        "escalate_nonresponse": {"allocation_approved"},
    },
    "recovery-verifier": {"verify_recovery": {"response_verified"}},
}


class OneAdvisoryRuntimeAgent:
    def __init__(self, role: str = ROLE, armor: Any | None = None):
        if role not in COMMAND_STATES:
            raise ValueError(f"unsupported role: {role}")
        self.role = role
        self.armor = armor or StructuralGuard()

    def query(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = payload or {}
        guard = self.armor.screen_request(body)
        command = str(body.get("expected_command") or "")
        status = str(body.get("status") or "")
        allowed = command in COMMAND_STATES[self.role] and status in COMMAND_STATES[self.role][command]
        return {
            "agent_role": self.role,
            "incident_id": body.get("incident_id"),
            "status_observed": status,
            "proposed_command": command if allowed else None,
            "allowed": allowed,
            "reason": "registered role and workflow state matched" if allowed else "command or state outside registered capability",
            "guardrails": {"request": guard, "response": {"screened": True, "control": "typed-command-schema"}},
            "managed_security_boundary": {
                "gateway": "day-three-ingress",
                "model_armor_templates": ["one-advisory-agent-input", "one-advisory-agent-output"],
                "inline_model_armor_claimed": False,
            },
        }


root_agent = OneAdvisoryRuntimeAgent()
