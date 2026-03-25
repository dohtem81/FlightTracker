from typing import Protocol

from .models import AircraftState


class StateRepository(Protocol):
    def connect(self) -> None: ...

    def close(self) -> None: ...

    @property
    def is_ready(self) -> bool: ...

    def write_states(self, states: list[AircraftState], source_time: int | None, grid_name: str) -> None: ...

    def read_states(self, limit: int) -> list[dict]: ...


class OpenSkyGateway(Protocol):
    async def pull_states(self) -> tuple[int | None, list[AircraftState]]: ...
