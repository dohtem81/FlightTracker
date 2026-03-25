# API

## Reader API
Base URL: `http://localhost:8010`

### `GET /health`
Purpose: service liveness and mode introspection.

Example response:
```json
{
  "status": "ok",
  "mode": "reader",
  "grid": null,
  "cassandra_connected": true
}
```

### `GET /api/states?limit=200`
Purpose: fetch latest aircraft states from Cassandra.

Query parameters:
- `limit` (optional, integer): capped by backend max setting.

Example response shape:
```json
{
  "source_time": null,
  "last_pull_epoch": 1774420377,
  "count": 3,
  "states": [
    {
      "icao24": "801526",
      "callsign": "AKJ500Z",
      "latitude": 19.4079,
      "longitude": 73.0055,
      "true_track": 73.71,
      "velocity": 187.05,
      "grid": "asia_pacific"
    }
  ]
}
```

## Collector Behavior
Collectors expose `GET /health` but are not intended as public data APIs for the frontend.
