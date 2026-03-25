import asyncio

import httpx

from ..domain.ports import OpenSkyGateway, StateRepository
from ..infrastructure.settings import AppSettings


class CollectorService:
    def __init__(self, settings: AppSettings, opensky_gateway: OpenSkyGateway, repository: StateRepository) -> None:
        self._settings = settings
        self._opensky_gateway = opensky_gateway
        self._repository = repository

    async def run_forever(self) -> None:
        async with httpx.AsyncClient(timeout=self._settings.request_timeout_seconds) as client:
            while True:
                try:
                    source_time, states = await self._opensky_gateway.pull_states(client)
                    await asyncio.to_thread(self._repository.write_states, states, source_time, self._settings.grid_name)
                except Exception as exc:
                    print(f"Collector cycle failed for {self._settings.grid_name}: {exc}")
                await asyncio.sleep(self._settings.poll_interval_seconds)
