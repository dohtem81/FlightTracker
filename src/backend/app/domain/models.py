from dataclasses import dataclass
from typing import Any


@dataclass
class AircraftState:
    icao24: str
    callsign: str | None
    origin_country: str | None
    time_position: int | None
    last_contact: int | None
    longitude: float
    latitude: float
    baro_altitude: float | None
    on_ground: bool | None
    velocity: float | None
    true_track: float | None
    vertical_rate: float | None
    geo_altitude: float | None
    squawk: str | None
    spi: bool | None
    position_source: int | None
    category: int | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "time_position": self.time_position,
            "last_contact": self.last_contact,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "baro_altitude": self.baro_altitude,
            "on_ground": self.on_ground,
            "velocity": self.velocity,
            "true_track": self.true_track,
            "vertical_rate": self.vertical_rate,
            "geo_altitude": self.geo_altitude,
            "squawk": self.squawk,
            "spi": self.spi,
            "position_source": self.position_source,
            "category": self.category,
        }
