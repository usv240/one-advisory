# Release audit — 2026-08-22

This release turns managed infrastructure into part of the primary incident path.

- `POST /api/demo/full` performs live, fail-closed Gemini 3.5 Flash advisory extraction in deployed mode.
- Gemini Embedding 001 ranks differentiated facility playbook processing; it cannot create public-health instructions or allocate resources.
- Four managed Agent Runtime roles now propose typed, state-bound commands. The Cloud Run orchestrator validates role, runtime, state, command, bounded retry, and receipt; rejection or outage fails closed.
- The full workflow invokes all four roles across six operational gates: fleet activation, policy rejection, standing playbook delivery, conflict detection, nonresponse escalation, and recovery verification.
- Every incident exposes `/api/incidents/{incident_id}/trace`; prompts, hidden reasoning, credentials, personal data, and stack traces are excluded.
- The separate `/api/platform` evidence endpoint continues to verify Registry, Runtime, Agent Identity, Gateway, and Model Armor resources live.
- Bonus publication and stakeholder validation remain unclaimed until real public URLs and consented sessions exist.

The remaining Stage 1 blocker is entrant-owned: attach a public, narrated, under-four-minute YouTube or Vimeo demo URL before submission.
