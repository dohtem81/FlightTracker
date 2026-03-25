import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .application.collector_service import CollectorService
from .application.reader_service import ReaderService
from .infrastructure.cassandra_repository import CassandraStateRepository
from .infrastructure.opensky_client import OpenSkyClient
from .infrastructure.settings import AppSettings
from .infrastructure.token_provider import TokenProvider
from .presentation.routes import build_router


def create_app() -> FastAPI:
    settings = AppSettings.load()

    repository = CassandraStateRepository(settings)
    token_provider = TokenProvider(settings)
    opensky_gateway = OpenSkyClient(settings, token_provider)

    collector_service = CollectorService(settings, opensky_gateway, repository)
    reader_service = ReaderService(repository)

    app = FastAPI(title="FlightTracker Backend", version="0.3.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    collector_task: asyncio.Task[None] | None = None

    @app.on_event("startup")
    async def on_startup() -> None:
        nonlocal collector_task
        await asyncio.to_thread(repository.connect)
        if settings.app_mode == "collector":
            collector_task = asyncio.create_task(collector_service.run_forever())

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        nonlocal collector_task
        if collector_task is not None:
            collector_task.cancel()
            try:
                await collector_task
            except asyncio.CancelledError:
                pass
        await asyncio.to_thread(repository.close)

    app.include_router(
        build_router(
            settings=settings,
            reader_service=reader_service,
            cassandra_connected=lambda: repository.is_ready,
        )
    )

    return app


app = create_app()
