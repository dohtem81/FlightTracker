import asyncio
from datetime import datetime
from typing import Any

from ..domain.ports import StateRepository


class ReaderService:
    def __init__(self, repository: StateRepository) -> None:
        self._repository = repository

    async def get_states(self, limit: int) -> dict[str, Any]:
        rows = await asyncio.to_thread(self._repository.read_states, limit)
        items: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["grid"] = item.get("grid_name")
            items.append(item)

        return {
            "source_time": None,
            "last_pull_epoch": int(datetime.utcnow().timestamp()),
            "count": len(items),
            "states": items,
        }
