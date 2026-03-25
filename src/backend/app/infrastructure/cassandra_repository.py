from threading import Lock
from typing import Any

from cassandra import InvalidRequest
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

from ..domain.models import AircraftState
from .settings import AppSettings


class CassandraStateRepository:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self.cluster: Cluster | None = None
        self.session = None
        self._is_ready = False
        self._schema_lock = Lock()

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    def _ensure_schema(self, session) -> None:
        session.execute(
            f"""
            CREATE KEYSPACE IF NOT EXISTS {self._settings.cassandra_keyspace}
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': {self._settings.cassandra_replication_factor}}}
            """
        )
        session.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self._settings.cassandra_keyspace}.latest_states (
                icao24 text PRIMARY KEY,
                callsign text,
                origin_country text,
                time_position bigint,
                last_contact bigint,
                longitude double,
                latitude double,
                baro_altitude double,
                on_ground boolean,
                velocity double,
                true_track double,
                vertical_rate double,
                geo_altitude double,
                squawk text,
                spi boolean,
                position_source int,
                category int,
                grid_name text,
                source_time bigint,
                updated_at timestamp
            )
            """
        )

        if self.cluster is not None:
            self.cluster.control_connection.wait_for_schema_agreement(wait_time=10)

    def connect(self) -> None:
        self.cluster = Cluster(contact_points=self._settings.cassandra_contact_points, port=self._settings.cassandra_port)
        session = self.cluster.connect()
        session.row_factory = dict_factory
        self._ensure_schema(session)
        self.session = session
        self._is_ready = True

    def close(self) -> None:
        if self.cluster is not None:
            self.cluster.shutdown()
        self.cluster = None
        self.session = None
        self._is_ready = False

    def write_states(self, states: list[AircraftState], source_time: int | None, grid_name: str) -> None:
        if not self.session:
            raise RuntimeError("Cassandra session is not initialized")

        def _do_write() -> None:
            for state in states:
                payload = state.as_dict()
                self.session.execute(
                    f"""
                    INSERT INTO {self._settings.cassandra_keyspace}.latest_states (
                        icao24, callsign, origin_country, time_position, last_contact,
                        longitude, latitude, baro_altitude, on_ground, velocity,
                        true_track, vertical_rate, geo_altitude, squawk, spi,
                        position_source, category, grid_name, source_time, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, toTimestamp(now())
                    )
                    """,
                    (
                        payload.get("icao24"),
                        payload.get("callsign"),
                        payload.get("origin_country"),
                        payload.get("time_position"),
                        payload.get("last_contact"),
                        payload.get("longitude"),
                        payload.get("latitude"),
                        payload.get("baro_altitude"),
                        payload.get("on_ground"),
                        payload.get("velocity"),
                        payload.get("true_track"),
                        payload.get("vertical_rate"),
                        payload.get("geo_altitude"),
                        payload.get("squawk"),
                        payload.get("spi"),
                        payload.get("position_source"),
                        payload.get("category"),
                        grid_name,
                        source_time,
                    ),
                )

        try:
            _do_write()
        except InvalidRequest as exc:
            if "table latest_states does not exist" not in str(exc).lower():
                raise
            with self._schema_lock:
                self._ensure_schema(self.session)
            _do_write()

    def read_states(self, limit: int) -> list[dict[str, Any]]:
        if not self.session:
            raise RuntimeError("Cassandra session is not initialized")

        safe_limit = max(1, min(limit, self._settings.max_aircraft_returned))
        rows = self.session.execute(
            f"SELECT * FROM {self._settings.cassandra_keyspace}.latest_states LIMIT {safe_limit}"
        )
        return list(rows)
