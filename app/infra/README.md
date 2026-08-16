# One Advisory cloud infrastructure

The checked-in composite indexes support transactional acknowledgement and recovery wake scans. `provision_scheduler.ps1` creates or updates the minute-level OIDC Cloud Scheduler worker. The application authenticates the dedicated scheduler identity before claiming Firestore work, and unauthenticated calls fail closed.

## Managed enterprise platform

- `register_agents.py` idempotently registers the four scoped REST capabilities.
- `deploy_runtimes.py` deploys the four scale-to-zero Agent Runtime resources with distinct Agent Identities and the governed shared client-to-agent MCP Gateway binding.
- `provision_platform.ps1` provisions the regional request and response Model Armor templates and calls the deployment scripts.
- `/api/platform` reads the managed control plane live and returns an explicit failure if it cannot verify the resources.

The public service uses synthetic facility data and sandbox contacts only. Logical workflow roles are not misrepresented as separately deployed agents; the four managed services correspond to the four explicitly registered capabilities.
