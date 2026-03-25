import json
import os
from dataclasses import dataclass
from typing import Any

import yaml


@dataclass
class AppSettings:
    app_mode: str
    opensky_url: str
    opensky_auth_url: str
    opensky_client_id: str
    opensky_client_secret: str
    token_refresh_margin: int
    grid_name: str
    grid_lat_min: float
    grid_lat_max: float
    grid_lon_min: float
    grid_lon_max: float
    poll_interval_seconds: int
    request_timeout_seconds: float
    max_aircraft_returned: int
    reader_default_limit: int
    frontend_request_limit: int
    frontend_refresh_interval_ms: int
    cassandra_contact_points: list[str]
    cassandra_port: int
    cassandra_keyspace: str
    cassandra_replication_factor: int

    @classmethod
    def load(cls) -> "AppSettings":
        config_path = os.getenv("APP_CONFIG_PATH", "/app/config/app-config.yml")
        config = _load_yaml_config(config_path)

        opensky_client_id, opensky_client_secret = _load_credentials()

        app_mode = os.getenv("APP_MODE", str(_cfg_get(config, ["backend", "app_mode_default"], "collector"))).strip().lower()
        if app_mode not in {"collector", "reader"}:
            app_mode = "collector"

        contact_points_cfg = _cfg_get(config, ["backend", "cassandra", "contact_points"], ["cassandra1", "cassandra2", "cassandra3"])
        default_contact_points = ",".join(contact_points_cfg) if isinstance(contact_points_cfg, list) else "cassandra1,cassandra2,cassandra3"
        cassandra_contact_points = [
            host.strip()
            for host in os.getenv("CASSANDRA_CONTACT_POINTS", default_contact_points).split(",")
            if host.strip()
        ]

        return cls(
            app_mode=app_mode,
            opensky_url=os.getenv(
                "OPENSKY_URL",
                str(_cfg_get(config, ["backend", "opensky", "states_api_url"], "https://opensky-network.org/api/states/all")),
            ),
            opensky_auth_url=os.getenv(
                "OPENSKY_AUTH_URL",
                str(
                    _cfg_get(
                        config,
                        ["backend", "opensky", "oauth_token_url"],
                        "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token",
                    )
                ),
            ),
            opensky_client_id=opensky_client_id,
            opensky_client_secret=opensky_client_secret,
            token_refresh_margin=int(
                os.getenv(
                    "TOKEN_REFRESH_MARGIN",
                    str(_cfg_get(config, ["backend", "opensky", "token_refresh_margin_seconds"], 30)),
                )
            ),
            grid_name=os.getenv("GRID_NAME", str(_cfg_get(config, ["backend", "collector", "grid_defaults", "name"], "global"))),
            grid_lat_min=float(
                os.getenv("GRID_LAT_MIN", str(_cfg_get(config, ["backend", "collector", "grid_defaults", "lat_min"], -90)))
            ),
            grid_lat_max=float(
                os.getenv("GRID_LAT_MAX", str(_cfg_get(config, ["backend", "collector", "grid_defaults", "lat_max"], 90)))
            ),
            grid_lon_min=float(
                os.getenv("GRID_LON_MIN", str(_cfg_get(config, ["backend", "collector", "grid_defaults", "lon_min"], -180)))
            ),
            grid_lon_max=float(
                os.getenv("GRID_LON_MAX", str(_cfg_get(config, ["backend", "collector", "grid_defaults", "lon_max"], 180)))
            ),
            poll_interval_seconds=int(
                os.getenv("POLL_INTERVAL_SECONDS", str(_cfg_get(config, ["backend", "collector", "poll_interval_seconds"], 10)))
            ),
            request_timeout_seconds=float(
                os.getenv(
                    "REQUEST_TIMEOUT_SECONDS",
                    str(_cfg_get(config, ["backend", "collector", "request_timeout_seconds"], 15)),
                )
            ),
            max_aircraft_returned=int(
                os.getenv(
                    "MAX_AIRCRAFT_RETURNED",
                    str(_cfg_get(config, ["backend", "collector", "max_aircraft_returned"], 10000)),
                )
            ),
            reader_default_limit=int(
                os.getenv(
                    "READER_DEFAULT_LIMIT",
                    str(_cfg_get(config, ["backend", "reader", "default_limit"], 200)),
                )
            ),
            frontend_request_limit=int(
                os.getenv(
                    "FRONTEND_REQUEST_LIMIT",
                    str(_cfg_get(config, ["frontend", "data_source", "request_limit"], 5000)),
                )
            ),
            frontend_refresh_interval_ms=int(
                os.getenv(
                    "FRONTEND_REFRESH_INTERVAL_MS",
                    str(_cfg_get(config, ["frontend", "data_source", "refresh_interval_ms"], 12000)),
                )
            ),
            cassandra_contact_points=cassandra_contact_points,
            cassandra_port=int(os.getenv("CASSANDRA_PORT", str(_cfg_get(config, ["backend", "cassandra", "port"], 9042)))),
            cassandra_keyspace=os.getenv("CASSANDRA_KEYSPACE", str(_cfg_get(config, ["backend", "cassandra", "keyspace"], "flighttracker"))),
            cassandra_replication_factor=int(
                os.getenv(
                    "CASSANDRA_REPLICATION_FACTOR",
                    str(_cfg_get(config, ["backend", "cassandra", "replication_factor"], 3)),
                )
            ),
        )


def _load_yaml_config(path: str) -> dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            return {}
        return data


def _cfg_get(config: dict[str, Any], keys: list[str], default: Any) -> Any:
    current: Any = config
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _load_credentials() -> tuple[str, str]:
    client_id = os.getenv("OPENSKY_CLIENT_ID", "")
    client_secret = os.getenv("OPENSKY_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        creds_path = "/app/config/credentials.json"
        if os.path.exists(creds_path):
            with open(creds_path, "r", encoding="utf-8") as f:
                creds = json.load(f)
                client_id = creds.get("clientId", client_id)
                client_secret = creds.get("clientSecret", client_secret)

    return client_id, client_secret
