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
        result = agent.query(payload={"verification": "synthetic-read-only"})
        guards = result.get("guardrails", {})
        if not (
            guards.get("request", {}).get("screened")
            and guards.get("response", {}).get("screened")
            and result.get("invoked", "").startswith("/api/")
        ):
            raise RuntimeError(f"bounded contract not proven for {runtime['role']}")
        if result.get("managed_security_boundary", {}).get(
            "inline_model_armor_claimed"
        ):
            raise RuntimeError("runtime made an unsupported inline Model Armor claim")
        summaries.append(
            {
                "role": result.get("agent_role"),
                "invoked": result.get("invoked"),
                "request_control": guards["request"]["control"],
                "response_control": guards["response"]["control"],
            }
        )
    print(json.dumps({"passed": len(summaries), "runtimes": summaries}, indent=2))


if __name__ == "__main__":
    main()
