import asyncio
from datetime import datetime, timedelta

import httpx

from .settings import AppSettings


class TokenProvider:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._lock = asyncio.Lock()
        self._token: str | None = None
        self._expires_at: datetime | None = None

    async def get_valid_token(self, client: httpx.AsyncClient) -> str:
        async with self._lock:
            if self._token and self._expires_at and datetime.utcnow() < self._expires_at:
                return self._token
            return await self._refresh(client)

    async def _refresh(self, client: httpx.AsyncClient) -> str:
        if not self._settings.opensky_client_id or not self._settings.opensky_client_secret:
            raise ValueError("OPENSKY_CLIENT_ID and OPENSKY_CLIENT_SECRET environment variables required")

        response = await client.post(
            self._settings.opensky_auth_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._settings.opensky_client_id,
                "client_secret": self._settings.opensky_client_secret,
            },
        )
        response.raise_for_status()

        data = response.json()
        self._token = data["access_token"]
        expires_in = data.get("expires_in", 1800)
        self._expires_at = datetime.utcnow() + timedelta(seconds=expires_in - self._settings.token_refresh_margin)
        return self._token
