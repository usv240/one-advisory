# Rules compliance — One Advisory

| Rules.md requirement | Evidence | Status |
|---|---|---|
| One category | The Fortified Enterprise Fleet | Pass |
| Gemini 3.5+ | Deployed `/api/demo/full` live fail-closed Gemini 3.5 Flash receipt, plus adjacent truth/accuracy files | Pass |
| Google agent framework | Google Gen AI SDK plus Vertex AI Agent Engine SDK | Pass |
| Google Cloud service | Cloud Run, Firestore, Cloud Trace, Agent Registry and Agent Runtime | Pass |
| Catalog and discovery | Four live Google Cloud Agent Registry services | Pass |
| Long-running state | Transactional Firestore acknowledgement wakes, bounded retry and cross-session incident memory | Pass |
| Managed runtime and identity | Four scale-to-zero Agent Runtime resources with four unique Agent Identities | Pass |
| Gateway and policy | All runtimes use the shared managed client-to-agent MCP gateway; typed command schemas are role- and state-bounded and gate the primary workflow | Pass |
| Model guardrails | Two regional Model Armor templates are live; runtimes enforce structural bounds; inline attachment is not claimed | Pass with explicit boundary |
| Observability | OpenTelemetry/Cloud Trace request correlation and ordered incident audit | Pass |
| Public repository | https://github.com/usv240/one-advisory | Pass |
| Reproducible setup and diagram | README, infra scripts, Dockerfile, indexes, `docs/architecture.svg` | Pass |
| Under-four-minute public video | Must be published by entrant with live fleet and Google Cloud evidence | Entrant action |
| Additional Google AI model | Gemini Embedding 001 performs operational semantic routing; claim only with a live `semantic_routing` receipt | Implemented; live evidence recorded |
| Optional public content/social post | Drafts are in `docs/`; eligible platform publication remains entrant action | Entrant action |

All facilities, people, advisories, allocations and contacts are fictional or sandboxed. The service does not issue public-health guidance.

## Additional production evidence

| Requirement | Implementation | Status |
|---|---|---|
| Self-service integration | Keyless judge UI plus protected `/v1`, no account required, 50 requests per key and network per UTC day | Pass |
| Secure public endpoint | HMAC-only keys, fingerprint-only IP handling, Secret Manager pepper, atomic Firestore quota transactions | Pass |
| Visible autonomy | Cumulative trace-derived receipt, direct proof endpoint, zero continue-click count, honest synthetic-event disclosure | Pass |