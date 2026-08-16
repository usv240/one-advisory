# One Advisory: Prize-Quality Build Plan

**Track:** The Fortified Enterprise Fleet  
**Product promise:** A warning is delivered once. One Advisory verifies that every critical facility completes the right operational response.  
**Primary user:** A local public-health or emergency-management coordinator.  
**Status:** Approved for implementation with a strict post-notification scope.

## 1. The precise friction

Utilities can map an affected zone, identify customers, issue notices, and document delivery.
Delivery is not the same as operational response. A dialysis clinic, school, and long-term-care
facility must interpret the same advisory differently, coordinate people and supplies, prove that
critical actions occurred, and reverse temporary controls when the advisory is rescinded.

One Advisory begins after an authorized advisory exists. It does not decide whether to issue one.

## 2. Defensible differentiation

Current platforms such as UOMS already cover zone definition, critical-customer identification,
notifications, approval logs, and rescission. One Advisory must not duplicate or claim those as its
innovation. Its contribution is the **last institutional mile**:

```text
authorized advisory
  -> affected critical facilities
  -> facility-specific operational playbooks
  -> approved tasks and resource requests
  -> acknowledgement plus evidence
  -> escalation and conflict resolution
  -> verified recovery after rescission
```

The demo covers exactly three facility classes: dialysis, school/childcare, and long-term care.
Depth and auditability matter more than a long facility list.

## 3. Research and implementation sources

| Design claim | Source and use |
|---|---|
| Different facilities and vulnerable populations require distinct advisory communication and planning | [CDC Drinking Water Advisory Communication Toolkit](https://www.cdc.gov/water-emergency/php/dwact/index.html) — facility taxonomy and planning structure |
| Critical-customer lists include hospitals, dialysis, schools, nursing homes, food facilities, and special-needs customers | [CDC complete DWACT PDF](https://www.cdc.gov/water-emergency/media/pdfs/2024/08/DWACT-2016.pdf) — facility registry fields and pre-incident preparation |
| A prolonged outage exposed communication, alternative-water, institutional, and interagency gaps | [CDC MMWR, Alabama water-system failure](https://www.cdc.gov/mmwr/preview/mmwrhtml/mm6006a1.htm) — problem evidence and tabletop scenario |
| Loss of potable water affected dialysis, surgery, infection control, food, cleaning, and other hospital functions | [West Virginia hospital response study](https://pmc.ncbi.nlm.nih.gov/articles/PMC5587347/) — operational-dependency model |
| Hemodialysis uses large water volumes and requires specific water-quality controls | [CDC, Water Use in Dialysis](https://www.cdc.gov/dialysis-safety/hcp/recommendations-resources/water-use-in-dialysis.html) — criticality and boundary |
| Zone, approval, notification, audit, and rescission are already implemented commercially | [UOMS Boil Water Notice Workflows](https://uoms.canopymapping.co/boil-water-notice-management-software) — prior art boundary |

Official guidance is retrieved and versioned; generated tasks retain source snippets. The demo uses
synthetic facilities and an authorized synthetic advisory.

## 4. End-to-end product flow

1. An authorized synthetic advisory arrives with type, zone, effective time, source, and approver.
2. The coordinator verifies the source and activates response.
3. Registry Agent intersects the zone with synthetic critical facilities and retrieves contacts,
   dependencies, approved playbooks, accessibility needs, and previous unresolved findings.
4. Policy Agent selects only source-backed playbook steps appropriate to the advisory type.
5. Dialysis, School/Childcare, and Long-Term-Care agents create facility-specific task proposals.
6. A human incident commander approves outbound instructions.
7. Contact Agent sends sandbox notifications and records delivery status.
8. Facility users acknowledge, attach evidence, request assistance, or report a constraint.
9. Resource Agent detects competing requests for a limited emergency-water delivery and proposes
   options; an authorized human chooses the allocation.
10. Escalation Agent raises non-response and missed-deadline cases.
11. On authorized rescission, Recovery Agent issues facility-specific recovery checks.
12. Audit Agent produces a complete, source-bearing after-action record.

## 5. Safety and authority contract

- The system cannot issue or rescind a public advisory.
- It cannot order evacuation, close a facility, allocate scarce resources, or certify compliance.
- Every consequential recommendation names its source and uncertainty.
- Missing jurisdiction, facility type, source, or approval creates a safe stop.
- Instructions are proposals until an authorized official approves them.
- Synthetic public demo data contains no real facility vulnerabilities or contact information.
- Facility roles see only the minimum information required for their tasks.

## 6. Fleet architecture

- FastAPI service on Cloud Run.
- Gemini 3.5 Flash through Vertex AI / Google Gen AI SDK for bounded advisory and evidence reading.
- Firestore-compatible stores for facilities, playbooks, incidents, tasks, approvals, evidence, and history.
- Cloud Scheduler-compatible wake scanner for acknowledgement deadlines and recovery checks.
- OpenTelemetry-compatible traces and structured audit events.
- Versioned agent registry describing capability, source scope, input/output schema, allowed tools,
  approval requirements, and data classification.
- Policy gateway rejects unregistered agents, unsupported facility classes, untrusted instructions,
  missing sources, and actions outside role scope.
- Persistent facility memory stores structured operational facts, not chat transcripts.
- Replay fixtures provide deterministic, no-cost evaluation and public demos.

## 7. Judge and first-user experience

The home screen is an incident-command workspace, not a chatbot. A map and incident header provide
orientation; a facility-response matrix makes completion and risk visible without color dependence.
The most important number is "verified responses / affected critical facilities." The interface
separates proposed, approved, delivered, acknowledged, evidenced, escalated, and recovered states.

The signature demo moment is a resource conflict: two agents request the final delivery slot, the
fleet surfaces the conflict with evidence, and a human makes the allocation.

## 8. Evaluation

- Facility intersection and classification accuracy.
- Task-to-source grounding completeness.
- Zero unsupported instructions.
- Zero consequential outbound actions before approval.
- Role and data-scope enforcement.
- Idempotent notification and evidence ingestion.
- Durable acknowledgement and escalation wakes.
- Resume after process interruption.
- Recovery checks tied to the correct advisory version.
- WCAG 2.2 AA in both themes and responsive layouts.
- Executable local and deployed demo flows.

No claim that the system prevents illness, closes facilities faster, or improves outcomes will be
made without field validation.

## 9. Four-minute demo spine

1. Activate an already-authorized synthetic advisory by drawing/selecting its zone.
2. Show three critical facilities discovered with different dependencies.
3. Open the source-grounded task proposals and approve them.
4. Show notifications, one acknowledgement, one evidence upload, and one non-response escalation.
5. Trigger two competing emergency-water requests; resolve the conflict as incident commander.
6. Rescind the advisory and complete differentiated recovery checks.
7. Open registry, policy rejection, persistent history, and audit trace.
8. End with deployed proof, evaluation results, limitations, and prior-art distinction.

## 10. Release gates

- Exact post-notification scope is visible on every public description.
- Three facility workflows are deep, source-bearing, and testable.
- At least one deliberate policy rejection appears in the demo.
- At least one cross-agent resource conflict requires human authority.
- All claims, tasks, and evidence retain provenance.
- Public Cloud Run service, deployment proof, architecture diagram, README, differentiation,
  validation report, and submission kit are complete.

