"""Create or update four One Advisory managed Agent Runtime capabilities."""
from __future__ import annotations

import os

import vertexai

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "agentic-fleet-2026")
LOCATION = os.getenv("REGION", "us-central1")
BACKEND_URL = os.getenv(
    "ONE_ADVISORY_BACKEND_URL",
    "https://one-advisory-109051079423.us-central1.run.app",
)
GATEWAY = os.getenv(
    "AGENT_GATEWAY",
    f"projects/{PROJECT_ID}/locations/{LOCATION}/agentGateways/day-three-ingress",
)
ROLES = {
    "facility-fleet": "Discovers differentiated source-bearing facility work.",
    "policy-gateway": "Rejects actions outside registered human authority.",
    "resource-coordinator": "Surfaces conflicts and options without allocating.",
    "recovery-verifier": "Verifies recovery, failures, and durable wake safeguards.",
}
QUERY_SCHEMA = [
    {
        "name": "query",
        "api_mode": "",
        "parameters": {
            "type": "object",
            "properties": {
                "payload": {
                    "type": "object",
                    "description": "Latest bounded request, screened before use.",
                }
            },
        },
    }
]


def source_config() -> dict:
    return {
        "source_packages": ["infra"],
        "entrypoint_module": "infra.runtime_agent",
        "entrypoint_object": "root_agent",
        "requirements_file": "infra/runtime_requirements.txt",
        "class_methods": QUERY_SCHEMA,
        "agent_framework": "custom",
        "python_version": "3.12",
    }


def main() -> None:
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)
    for role, description in ROLES.items():
        display_name = f"One Advisory Runtime {role}"
        existing = list(
            client.agent_engines.list(
                config={"filter": f'display_name="{display_name}"'}
            )
        )
        if existing:
            name = existing[0].api_resource.name
            remote = client.agent_engines.update(name=name, config=source_config())
            print(f"updated: {role}: {remote.api_resource.name}")
            continue
        config = {
            **source_config(),
            "display_name": display_name,
            "description": description,
            "env_vars": {
                "ONE_ADVISORY_AGENT_ROLE": role,
                "ONE_ADVISORY_BACKEND_URL": BACKEND_URL,
                "MODEL_ARMOR_REQUEST_TEMPLATE": "one-advisory-agent-input",
                "MODEL_ARMOR_RESPONSE_TEMPLATE": "one-advisory-agent-output",
            },
            "identity_type": vertexai.types.IdentityType.AGENT_IDENTITY,
            "agent_gateway_config": {
                "client_to_agent_config": {"agent_gateway": GATEWAY}
            },
            "min_instances": 0,
            "max_instances": 1,
            "container_concurrency": 10,
            "labels": {
                "hackathon": "all-things-agentic",
                "project": "one-advisory",
                "role": role,
            },
        }
        remote = client.agent_engines.create(config=config)
        print(f"created: {role}: {remote.api_resource.name}")


if __name__ == "__main__":
    main()
