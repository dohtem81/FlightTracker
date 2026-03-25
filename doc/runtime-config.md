# Runtime Configuration

Canonical config file: `config/app-config.yml`

Backend reads this file at startup (`/app/config/app-config.yml` in containers), then applies environment variable overrides.

## Override Rule
1. Environment variable value (if set).
2. YAML config value.
3. Hardcoded fallback in code.

## Important Keys

### Backend
- `backend.app_mode_default`
- `backend.opensky.states_api_url`
- `backend.opensky.oauth_token_url`
- `backend.opensky.token_refresh_margin_seconds`
- `backend.collector.poll_interval_seconds`
- `backend.collector.request_timeout_seconds`
- `backend.collector.max_aircraft_returned`
- `backend.collector.grid_defaults.*`
- `backend.cassandra.contact_points`
- `backend.cassandra.port`
- `backend.cassandra.keyspace`
- `backend.cassandra.replication_factor`

### Frontend (documented values)
- `frontend.data_source.*`
- `frontend.map.*`
- `frontend.marker.*`
- `frontend.colors_by_grid.*`

## Secrets
OAuth credentials are intentionally separate from YAML and loaded from:
- environment vars `OPENSKY_CLIENT_ID` and `OPENSKY_CLIENT_SECRET`, or
- `config/credentials.json` (mounted into backend containers).

Keep credentials out of git.
