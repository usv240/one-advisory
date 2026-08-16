# One Advisory: As-Built Technical Design

## State and orchestration

One FastAPI service carries an incident through authorized receipt, fleet activation, proposed
tasks, human approval, facility response, resource conflict, human allocation, escalation,
rescission, recovery, and closure. Invalid ordering returns a conflict. The demo’s state is a
structured incident record rather than a replayed chat transcript.

Eight registered application roles declare version, allowed capability, approval requirement, and
data classification. They are independently testable policy boundaries, not a claim of physically
separate deployments.

## Model path

The advisory reader sends an authorized synthetic artifact to Gemini 3.5 Flash at the Vertex AI
global endpoint. It first requests a transcription, then a small JSON schema. Application code
keeps a field only when its quote occurs verbatim in that transcription and confidence is valid.
The model cannot issue, expand, reinterpret, or rescind the advisory.

## Authority and policy

- outbound facility work remains proposed until a named incident commander approves it;
- the generic close-all proposal is rejected as unsupported and outside system authority;
- a resource conflict produces options but no winner;
- a named human records the allocation;
- recovery begins only from an authorized rescission fixture;
- every public connector is synthetic and sandboxed.

## Data and deployment

Local mode uses copy-on-read memory storage. Deployment mode uses a Firestore adapter. The included
non-root Python 3.12 container is configured for Cloud Run. `/health`, `/api/proof`, and
`/api/conformance` expose environment, safeguards, and track mapping.

## Explicitly absent

Production notification, utility, facility, logistics, or emergency-management integrations;
real vulnerability/contact data; autonomous public-health authority; separate IAM agents; field
validation; a completed live-model recording; and validated outcome improvements.
