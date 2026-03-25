# Services

## Backend Services

### Backend process structure (`src/backend/app`)
- `main.py`: ASGI entrypoint only.
- `app.py`: dependency composition and FastAPI lifecycle.
- `presentation/routes.py`: HTTP endpoints.
- `application/*`: use-case orchestration.
- `domain/*`: entities and ports.
- `infrastructure/*`: OpenSky/Cassandra/config adapters.

### `api1`..`api6` (collectors)
- Runtime: Python + FastAPI process with background polling loop.
- Mode: `APP_MODE=collector`.
- Input: OpenSky `/api/states/all` with region bounds.
- Output: writes records into Cassandra `latest_states` table.
- Does not serve flight data to frontend (`/api/states` is collector-disabled).

### `api-read` (reader)
- Runtime: same backend image as collectors.
- Mode: `APP_MODE=reader`.
- Input: Cassandra `latest_states` table.
- Output: `GET /api/states` for UI clients.
- Exposed on host port `8010`.

## Data Store

### `cassandra1`, `cassandra2`, `cassandra3`
- Apache Cassandra 4.1 nodes.
- Keyspace initialized by backend on startup (`flighttracker` by default).
- Stores latest known state per aircraft (`icao24` primary key).

## Frontend Service

### `web`
- Runtime: `nginx:alpine` serving static assets from `src/`.
- UI stack: HTML/CSS/vanilla JS + Leaflet.
- Polls reader endpoint for aircraft states.
- Exposed on host port `8080`.
