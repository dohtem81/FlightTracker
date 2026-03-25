# Data Model

## Storage Model
Keyspace: `flighttracker` (configurable)

Table: `latest_states`

Purpose: keep latest known state per aircraft.

## Primary Key
- `icao24` (text) is the primary key.

Effect:
- New writes for the same aircraft overwrite previous row state.
- Table acts as a mutable latest snapshot set.

## Core Columns
- Identity: `icao24`, `callsign`, `origin_country`
- Position: `latitude`, `longitude`
- Flight state: `baro_altitude`, `geo_altitude`, `velocity`, `true_track`, `vertical_rate`, `on_ground`
- Timing: `time_position`, `last_contact`, `source_time`, `updated_at`
- Metadata: `squawk`, `spi`, `position_source`, `category`, `grid_name`

## Notes
- Reader API maps `grid_name` to `grid` in response payload.
- Current schema optimizes for live map view, not historical replay.
- For replay/time-travel features, add an append-only history table keyed by time.
