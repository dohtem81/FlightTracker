# FlightTracker

FlightTracker is a distributed flight-tracking platform with a write/read split:

- Collector services ingest OpenSky state vectors per world grid.
- Collectors persist latest aircraft state to Cassandra.
- A dedicated reader service serves frontend queries.
- A Leaflet-based web UI renders global aircraft positions.

## Current Architecture

```text
OpenSky API (OAuth2)
        |
        v
api1..api6 (collectors, grid-scoped)
        |
        v
Cassandra cluster (cassandra1..3)
        |
        v
api-read (reader API on :8010)
        |
        v
web (nginx static frontend on :8080)
```

## Service Roles

- `api1..api6`: collector-only workers (`APP_MODE=collector`), no frontend data serving.
- `api-read`: read service (`APP_MODE=reader`), serves `GET /api/states`.
- `web`: static frontend that polls reader API and draws markers on the world map.
- `cassandra1..3`: distributed datastore for latest aircraft state.

## Quick Start

### 1. Configure credentials
Create/update [config/credentials.json](config/credentials.json) with OpenSky OAuth2 client credentials:

```json
{
  "clientId": "your-opensky-client-id",
  "clientSecret": "your-opensky-client-secret"
}
```

### 2. Build and run

```powershell
docker compose up -d --build
```

### 3. Open services

- UI: `http://localhost:8080`
- Reader health: `http://localhost:8010/health`
- Reader states: `http://localhost:8010/api/states?limit=5`

## Configuration

- Canonical config reference: [config/app-config.yml](config/app-config.yml)
- Backend loads YAML defaults and allows environment overrides.
- Secrets are loaded from env vars or [config/credentials.json](config/credentials.json).

## Documentation

Detailed docs are in [doc/README.md](doc/README.md):

- [doc/architecture.md](doc/architecture.md)
- [doc/services.md](doc/services.md)
- [doc/api.md](doc/api.md)
- [doc/data-model.md](doc/data-model.md)
- [doc/runtime-config.md](doc/runtime-config.md)
- [doc/operations.md](doc/operations.md)

## Notes

- Current Cassandra model stores latest known row per `icao24`.
- For full historical replay, add an append-only history table keyed by time.
