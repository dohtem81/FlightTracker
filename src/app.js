const statusChip = document.getElementById("map-status");
const resetButton = document.getElementById("reset-view");
const colorModeToggle = document.getElementById("color-mode-toggle");

let colorByGridEnabled = false;

const gridServices = [
  { name: "north_america", color: "#FF6B6B" },
  { name: "europe_atlantic", color: "#4ECDC4" },
  { name: "asia_pacific", color: "#FFE66D" },
  { name: "south_america", color: "#95E1D3" },
  { name: "africa_indian", color: "#C7CEEA" },
  { name: "australia_pacific", color: "#FFA07A" },
];

const gridColorMap = new Map(gridServices.map((s) => [s.name, s.color]));

const readerBaseUrl = "http://localhost:8010";
let requestLimit = 5000;
let refreshIntervalMs = 12000;
let refreshTimer = null;

const defaultView = {
  center: [22, 8],
  zoom: 2,
};

const map = L.map("map", {
  worldCopyJump: true,
  minZoom: 2,
  maxBoundsViscosity: 1,
}).setView(defaultView.center, defaultView.zoom);

map.setMaxBounds([
  [-85, -180],
  [85, 180],
]);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

const aircraftLayer = L.layerGroup().addTo(map);

function getHeadingLineEnd(latitude, longitude, headingDegrees, lengthKm = 35) {
  const headingRad = (headingDegrees * Math.PI) / 180;
  const latDelta = (lengthKm / 110.574) * Math.cos(headingRad);
  const lonScale = 111.320 * Math.cos((latitude * Math.PI) / 180);
  const lonDelta = lonScale === 0 ? 0 : (lengthKm / lonScale) * Math.sin(headingRad);
  return [latitude + latDelta, longitude + lonDelta];
}

function markerLabel(state) {
  const callsign = state.callsign || "N/A";
  const altitude = state.geo_altitude ?? state.baro_altitude;
  const altitudeText = altitude == null ? "unknown" : `${Math.round(altitude)} m`;
  const speedText = state.velocity == null ? "unknown" : `${Math.round(state.velocity)} m/s`;
  const heading = state.true_track ?? state.track ?? "unknown";
  const headingText = heading === "unknown" ? "unknown" : `${Math.round(heading)}°`;
  const grid = state.grid ? `<br>Grid: ${state.grid}` : "";
  return `<strong>${callsign}</strong><br>ICAO24: ${state.icao24}<br>Alt: ${altitudeText}<br>Speed: ${speedText}<br>Heading: ${headingText}${grid}`;
}

async function refreshAircraft() {
  statusChip.textContent = "Syncing flights...";

  try {
    const response = await fetch(`${readerBaseUrl}/api/states?limit=${requestLimit}`, {
      cache: "no-store",
    });
    if (!response.ok) {
      throw new Error(`reader: ${response.status}`);
    }

    const data = await response.json();
    const allStates = data.states || [];

    aircraftLayer.clearLayers();
    allStates.forEach((state) => {
      if (state.latitude == null || state.longitude == null) {
        return;
      }

      const fillColor = colorByGridEnabled ? gridColorMap.get(state.grid) || "#ff8f3c" : "#ff8f3c";
      const marker = L.circleMarker([state.latitude, state.longitude], {
        radius: 7,
        weight: 1,
        color: "#8cf1ff",
        fillColor: fillColor,
        fillOpacity: 0.8,
      });

      const heading = state.true_track ?? state.track;
      if (typeof heading === "number" && Number.isFinite(heading)) {
        const [lineEndLat, lineEndLon] = getHeadingLineEnd(state.latitude, state.longitude, heading);
        L.polyline(
          [
            [state.latitude, state.longitude],
            [lineEndLat, lineEndLon],
          ],
          {
            color: fillColor,
            weight: 2,
            opacity: 0.9,
          }
        ).addTo(aircraftLayer);
      }

      marker.bindPopup(markerLabel(state));
      marker.addTo(aircraftLayer);
    });

    statusChip.textContent = `${allStates.length} flights (from Cassandra)`;
  } catch (error) {
    statusChip.textContent = "API unavailable";
    console.error("Unable to refresh aircraft states", error);
  }
}

async function loadUiConfig() {
  try {
    const response = await fetch(`${readerBaseUrl}/api/ui-config`, {
      cache: "no-store",
    });
    if (!response.ok) {
      throw new Error(`ui-config: ${response.status}`);
    }

    const data = await response.json();
    const cfg = data?.data_source || {};

    if (typeof cfg.request_limit === "number" && Number.isFinite(cfg.request_limit) && cfg.request_limit > 0) {
      requestLimit = Math.floor(cfg.request_limit);
    }
    if (typeof cfg.refresh_interval_ms === "number" && Number.isFinite(cfg.refresh_interval_ms) && cfg.refresh_interval_ms > 0) {
      refreshIntervalMs = Math.floor(cfg.refresh_interval_ms);
    }
  } catch (error) {
    console.warn("Unable to load UI config, using defaults", error);
  }
}

resetButton.addEventListener("click", () => {
  map.flyTo(defaultView.center, defaultView.zoom, {
    duration: 1,
  });
});

colorModeToggle.addEventListener("change", () => {
  colorByGridEnabled = colorModeToggle.checked;
  refreshAircraft();
});

setTimeout(() => {
  map.invalidateSize();
}, 150);

async function initialize() {
  await loadUiConfig();
  await refreshAircraft();
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
  refreshTimer = setInterval(refreshAircraft, refreshIntervalMs);
}

initialize();
