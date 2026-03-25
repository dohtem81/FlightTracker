# Architecture

## Overview
FlightTracker is a distributed flight data pipeline with a strict write/read split:

1. Collector services poll OpenSky for specific world grid regions.
2. Collectors write latest aircraft states into Cassandra.
3. A dedicated reader service exposes data to the frontend.
4. Web frontend renders global aircraft positions on a Leaflet map.

## Runtime Topology

```text
OpenSky API (OAuth2)
        |
        v
+------------------------------+
| 6 x Collector Services       |
| api1..api6 (APP_MODE=collector)
| - region-scoped polling      |
| - Cassandra writes only      |
+------------------------------+
        |
        v
+------------------------------+
| Cassandra Cluster            |
| cassandra1, cassandra2,      |
| cassandra3                   |
+------------------------------+
        |
        v
+------------------------------+
| Reader Service               |
| api-read (APP_MODE=reader)   |
| GET /api/states              |
+------------------------------+
        |
        v
+------------------------------+
| Web Frontend (nginx + JS)    |
| Leaflet map + overlays       |
+------------------------------+
```

## Backend Clean Architecture

Backend code is organized into explicit layers:

```text
app/
        main.py                  # Thin ASGI entrypoint (exports app)
        app.py                   # Composition root (wires dependencies)
        domain/
                models.py              # Core domain entities
                ports.py               # Repository/gateway interfaces
        application/
                collector_service.py   # Ingestion use case orchestration
                reader_service.py      # Read/query use case orchestration
        infrastructure/
                settings.py            # YAML + env config loading
                token_provider.py      # OAuth2 token lifecycle
                opensky_client.py      # OpenSky API adapter
                cassandra_repository.py# Cassandra adapter and schema bootstrap
        presentation/
                routes.py              # FastAPI routes and HTTP response mapping
```

Layer dependency direction:
- `presentation` depends on `application`.
- `application` depends on `domain` ports.
- `infrastructure` implements `domain` ports.
- `main.py` and `app.py` assemble concrete runtime wiring.

## Entrypoint Split
- `main.py`: minimal module used by Uvicorn (`app.main:app`).
- `app.py`: constructs settings, repository, external gateway, use-case services, routes, and lifecycle hooks.

This keeps framework bootstrap concerns out of business logic and makes test boundaries clearer.

## Service Roles
- Collector: ingest external flight states and persist to Cassandra. No frontend-serving responsibility.
- Reader: query Cassandra and return state snapshots to clients.
- Web: static UI shell that periodically fetches data from reader endpoint.

## Grid Partitioning
The world is split into 3x2 regions, one collector per region:
- north_america
- europe_atlantic
- asia_pacific
- south_america
- africa_indian
- australia_pacific

## Why This Split
- Better scaling: ingest and read paths can be tuned independently.
- Cleaner ownership: collectors are write-only workers.
- Safer operations: frontend load does not impact ingestion cycles.
- Easier extension: additional readers or analytics services can be added without changing collectors.
- Cleaner backend layering: domain/application logic remains isolated from infrastructure and HTTP wiring.
