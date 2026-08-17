"""Persistence adapters for One Advisory incidents."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Protocol


class IncidentStore(Protocol):
    def put(self, incident: dict[str, Any]) -> None: ...
    def get(self, incident_id: str) -> dict[str, Any] | None: ...
    def list_incidents(self) -> list[dict[str, Any]]: ...
    def clear(self) -> None: ...


class MemoryIncidentStore:
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def put(self, incident: dict[str, Any]) -> None:
        self._items[incident["incident_id"]] = deepcopy(incident)

    def get(self, incident_id: str) -> dict[str, Any] | None:
        item = self._items.get(incident_id)
        return deepcopy(item) if item is not None else None

    def list_incidents(self) -> list[dict[str, Any]]:
        return sorted((deepcopy(item) for item in self._items.values()), key=lambda item: item.get("created_at", ""), reverse=True)

    def clear(self) -> None:
        self._items.clear()


class FirestoreIncidentStore:
    def __init__(self, client: Any, collection: str = "one_advisory_incidents") -> None:
        self._collection = client.collection(collection)

    def put(self, incident: dict[str, Any]) -> None:
        self._collection.document(incident["incident_id"]).set(incident)

    def get(self, incident_id: str) -> dict[str, Any] | None:
        snapshot = self._collection.document(incident_id).get()
        return snapshot.to_dict() if snapshot.exists else None

    def list_incidents(self) -> list[dict[str, Any]]:
        return sorted((snapshot.to_dict() for snapshot in self._collection.stream()), key=lambda item: item.get("created_at", ""), reverse=True)

    def clear(self) -> None:
        for document in self._collection.stream():
            document.reference.delete()

