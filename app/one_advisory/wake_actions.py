from __future__ import annotations


class AdvisoryWakeExecutor:
    def __init__(self, store):
        self.store = store

    def execute(self, wake):
        incident = self.store.get(wake.run_id)
        if incident is None:
            raise ValueError(f"missing incident {wake.run_id}")
        actions = incident.setdefault("wake_actions", [])
        if any(row["wake_id"] == wake.wake_id for row in actions):
            return
        if wake.kind not in {"facility_ack_check", "recovery_verification"}:
            raise ValueError(f"unsupported wake kind {wake.kind}")
        actions.append({
            "wake_id": wake.wake_id,
            "kind": wake.kind,
            "result": "human_queue_prepared",
            "external_contact": False,
            "public_health_decision": None,
        })
        self.store.put(incident)

