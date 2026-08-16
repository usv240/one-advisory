# Rules compliance — One Advisory

| Rules.md requirement | Evidence | Status |
|---|---|---|
| One category | The Fortified Enterprise Fleet | Pass |
| Gemini 3.5+ | Live Vertex AI Gemini 3.5 Flash recording, adjacent truth and accuracy files | Pass |
| Google agent framework | Google Gen AI SDK plus Vertex AI Agent Engine SDK | Pass |
| Google Cloud service | Cloud Run, Firestore, Cloud Trace, Agent Registry and Agent Runtime | Pass |
| Catalog and discovery | Four live Google Cloud Agent Registry services | Pass |
| Long-running state | Transactional Firestore acknowledgement wakes, bounded retry and cross-session incident memory | Pass |
| Managed runtime and identity | Four scale-to-zero Agent Runtime resources with four unique Agent Identities | Pass |
| Gateway and policy | All runtimes use the shared managed client-to-agent MCP gateway; capability maps are GET-only | Pass |
| Model guardrails | Two regional Model Armor templates are live; runtimes enforce structural bounds; inline attachment is not claimed | Pass with explicit boundary |
| Observability | OpenTelemetry/Cloud Trace request correlation and ordered incident audit | Pass |
| Public repository | https://github.com/usv240/one-advisory | Pass |
| Reproducible setup and diagram | README, infra scripts, Dockerfile, indexes, `docs/architecture.svg` | Pass |
| Under-four-minute public video | Must be published by entrant with live fleet and Google Cloud evidence | Entrant action |
| Optional public content/social post | Drafts are in `docs/`; eligible platform publication remains entrant action | Entrant action |

All facilities, people, advisories, allocations and contacts are fictional or sandboxed. The service does not issue public-health guidance.
