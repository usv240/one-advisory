# One Advisory Developer API

The hosted UI remains keyless for judges. Integrations use the stable, authenticated `/v1` API.

## Get a free key

```bash
curl -X POST "$BASE_URL/api/developer/keys" \
  -H "Content-Type: application/json" \
  -d '{"label":"evaluation","acceptable_use_acknowledgement":true}'
```

The key is displayed once and valid for 180 days. Only an HMAC digest is persisted. A keyed network fingerprint—not a raw client address—is retained for abuse control. Both the key and originating network receive 50 requests per UTC day, enforced atomically in Firestore. Up to five keys may be issued per network per day, but they share that network ceiling. Rate-limit headers accompany every authenticated response.

## Use the service

```bash
curl -X POST "$BASE_URL/v1/tabletop-runs" -H "X-API-Key: $API_KEY"
```

For input-driven use, `POST /v1/incidents` with a fictional authorized advisory and the three typed facility records. Then send facility-update events, the named incident commander's allocation decision, and the authorized rescission event. The governed fleet auto-continues between those boundaries and uses the same managed Agent Runtime orchestrator as the product UI. Inspect `/docs`, the safe trace, or `GET /v1/incidents/{incident_id}/autonomy-proof`.

The public service accepts fictional synthetic exercise data only. It is not an authorized emergency notification system and cannot issue or rescind an advisory or allocate a scarce resource.

## Security and durability

- The HMAC pepper is injected from Google Secret Manager.
- Firestore transactions prevent concurrent quota bypass.
- No resource-list endpoint exposes another caller's records.
- Managed Agent Runtime command receipts, Cloud Trace spans, audit events, and durable Cloud Scheduler wakes make execution independently inspectable.

