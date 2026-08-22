"""Invoke all managed capabilities and require their bounded read-only contract."""
from __future__ import annotations

import json
from urllib.request import urlopen

import vertexai

PROJECT_ID = "agentic-fleet-2026"
LOCATION = "us-central1"
PLATFORM_URL = (
    "https://one-advisory-109051079423.us-central1.run.app/api/platform"
)


def main() -> None:
    with urlopen(PLATFORM_URL, timeout=30) as response:
        platform = json.loads(response.read().decode("utf-8"))
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)
    summaries = []
    for runtime in platform["runtimes"]:
        agent = client.agent_engines.get(name=runtime["name"])
        role = runtime["role"]
        commands = {"facility-fleet": ("authorized_advisory_received", "activate_fleet"), "policy-gateway": ("proposals_ready", "reject_unregistered_action"), "resource-coordinator": ("responses_in_progress", "detect_resource_conflict"), "recovery-verifier": ("response_verified", "verify_recovery")}
        status, command = commands[role]
        result = agent.query(payload={"incident_id": "synthetic-verification", "status": status, "expected_command": command})
        guards = result.get("guardrails", {})
        if not (
            guards.get("request", {}).get("screened")
            and guards.get("response", {}).get("screened")
            and result.get("allowed")
            and result.get("proposed_command") == command
        ):
            raise RuntimeError(f"bounded contract not proven for {runtime['role']}")
        if result.get("managed_security_boundary", {}).get(
            "inline_model_armor_claimed"
        ):
            raise RuntimeError("runtime made an unsupported inline Model Armor claim")
        summaries.append(
            {
                "role": result.get("agent_role"),
                "proposed_command": result.get("proposed_command"),
                "request_control": guards["request"]["control"],
                "response_control": guards["response"]["control"],
            }
        )
    print(json.dumps({"passed": len(summaries), "runtimes": summaries}, indent=2))


if __name__ == "__main__":
    main()
