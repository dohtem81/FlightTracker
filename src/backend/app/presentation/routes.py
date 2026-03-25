from typing import Any, Callable

from fastapi import APIRouter, HTTPException

from ..application.reader_service import ReaderService
from ..infrastructure.settings import AppSettings


def build_router(settings: AppSettings, reader_service: ReaderService, cassandra_connected: Callable[[], bool]) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "mode": settings.app_mode,
            "grid": settings.grid_name if settings.app_mode == "collector" else None,
            "cassandra_connected": cassandra_connected(),
        }

    @router.get("/api/states")
    async def get_states(limit: int = settings.reader_default_limit) -> dict[str, Any]:
        if settings.app_mode != "reader":
            raise HTTPException(status_code=404, detail="This instance is collector-only")
        return await reader_service.get_states(limit)

    @router.get("/api/ui-config")
    async def get_ui_config() -> dict[str, Any]:
        return {
            "data_source": {
                "reader_states_url": "http://localhost:8010/api/states",
                "request_limit": settings.frontend_request_limit,
                "refresh_interval_ms": settings.frontend_refresh_interval_ms,
            }
        }

    return router
