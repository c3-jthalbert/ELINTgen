# ELINTgen: Synthetic ELINT Generation

A lightweight Python toolkit for generating synthetic ELINT detections from AIS vessel tracks, designed for prototyping multi-INT fusion pipelines. It supports configurable sensor and emitter profiles, spatial error simulation, and interactive geospatial visualization.

> ⚠️ This code is intended for **research and prototyping purposes only**—not operational use.

---

## 🔧 Features

- **Spline-based track sampling** from AIS data
- **Probabilistic emitter modeling** with time-variable behavior
- **Configurable sensor error models**, including directional bias and elliptical uncertainty
- **Interactive mapping** with Plotly for AIS tracks, detection splines, and ELINT ellipses
- **GeoJSON filtering and masking** for spatial analysis

---

## 🗂 Module Overview

The package provides the following utilities:

| Component | Description |
|----------|-------------|
| `generate_elint_detections_from_spline` | Generate detections from spline-interpolated tracks |
| `SENSOR_PROFILES`, `EMITTER_PROFILES`  | Define detection behavior and emitter signal characteristics |
| `compute_bearing`, `offset_position`   | Geographic math utilities |
| `load_geojson`, `plot_geojson_file`    | Load and display GeoJSON regions |
| `mask_elint_by_geojson`                | Filter detections based on polygon overlap |
| `add_ais_tracks`, `add_spline`         | Plot AIS tracks and interpolated splines on a map |
| `add_elint_detections`                 | Visualize detections and their error ellipses |
| `init_map`                             | Initialize a Plotly Mapbox map view |

---

## 🚀 Quick Example

```python
from elintgen import (
    generate_elint_detections_from_spline,
    SENSOR_PROFILES,
    EMITTER_PROFILES
)
import pandas as pd

# Load AIS track data with Timestamp, Latitude, Longitude, TrackID
track_df = pd.read_csv("example_track.csv")

# Generate ELINT detections
elint_df, lat_spline, lon_spline = generate_elint_detections_from_spline(
    track_df,
    sensor_type="shore",
    emitter_type="military",
    sensor_profiles=SENSOR_PROFILES,
    emitter_profiles=EMITTER_PROFILES
)
```

---

## 📊 Visualization Example

```python
from elintgen import init_map, add_ais_tracks, add_elint_detections

fig = init_map()
fig = add_ais_tracks(track_df, fig=fig)
fig = add_elint_detections(elint_df, fig=fig)
fig.show()
```

---
