"""Tiny in-memory stand-in for the AsyncDatabase calls the seed uses."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UpdateResult:
    upserted_id: Any


@dataclass
class FakeCollection:
    docs: list[dict[str, Any]] = field(default_factory=list)
    indexes: list[Any] = field(default_factory=list)

    async def create_indexes(self, models: list[Any]) -> list[str]:
        self.indexes.extend(models)
        return [str(m) for m in models]

    async def update_one(self, query: dict, update: dict, upsert: bool = False) -> UpdateResult:
        for doc in self.docs:
            if all(doc.get(k) == v for k, v in query.items()):
                doc.update(update.get("$set", {}))
                return UpdateResult(upserted_id=None)
        if not upsert:
            return UpdateResult(upserted_id=None)
        new = {**query, **update.get("$setOnInsert", {}), **update.get("$set", {})}
        self.docs.append(new)
        return UpdateResult(upserted_id=len(self.docs))

    async def count_documents(self, query: dict) -> int:
        return len(self.docs)


class FakeDatabase(dict):
    def __missing__(self, name: str) -> FakeCollection:
        self[name] = FakeCollection()
        return self[name]
