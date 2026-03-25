from typing import Any

import httpx

from ..domain.models import AircraftState
from .settings import AppSettings
from .token_provider import TokenProvider


class OpenSkyClient:
    def __init__(self, settings: AppSettings, token_provider: TokenProvider) -> None:
        self._settings = settings
        self._token_provider = token_provider

    async def pull_states(self, client: httpx.AsyncClient) -> tuple[int | None, list[AircraftState]]:
        token = await self._token_provider.get_valid_token(client)
        params = {
            "lamin": self._settings.grid_lat_min,
            "lamax": self._settings.grid_lat_max,
            "lomin": self._settings.grid_lon_min,
            "lomax": self._settings.grid_lon_max,
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(self._settings.opensky_url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        source_time = data.get("time")
        rows = data.get("states") or []

        parsed: list[AircraftState] = []
        for row in rows:
            if not isinstance(row, list):
                continue
            item = _parse_state_vector(row)
            if item is None:
                continue
            parsed.append(item)
            if len(parsed) >= self._settings.max_aircraft_returned:
                break

        return source_time, parsed


def _parse_state_vector(row: list[Any]) -> AircraftState | None:
    if len(row) < 17:
        return None

    lon = row[5]
    lat = row[6]
    if lon is None or lat is None:
        return None

    return AircraftState(
        icao24=row[0],
        callsign=(row[1] or "").strip() or None,
        origin_country=row[2],
        time_position=row[3],
        last_contact=row[4],
        longitude=lon,
        latitude=lat,
        baro_altitude=row[7],
        on_ground=row[8],
        velocity=row[9],
        true_track=row[10],
        vertical_rate=row[11],
        geo_altitude=row[13],
        squawk=row[14],
        spi=row[15],
        position_source=row[16],
        category=row[17] if len(row) > 17 else None,
    )
