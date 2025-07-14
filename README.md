# ELINTgen: Synthetic ELINT Generation from Vessel Tracks

`ELINTgen` is a lightweight, modular Python toolkit for generating synthetic ELINT detections from real or simulated vessel tracks (e.g., AIS). It supports configurable sensor and emitter profiles, spatial error modeling, and interactive visualization, and is designed for prototyping multi-INT fusion pipelines.

> ⚠️ This code is intended for **research and prototyping purposes only** — not operational use.

---

## 🔧 Core Features

- Cubic spline interpolation of AIS tracks
- Configurable ELINT sensors (shore, satellite, drone)
- Emitter models for civilian, military, or dual-use behavior
- Positional error modeling with directional uncertainty
- Plotly-based visualization of tracks and detections
- GeoJSON filtering and masking for regional analysis
- YAML-driven scenario configuration and complexification

---

## 🗂️ Module Overview

| Component | Description |
|----------|-------------|
| `generate_elint_detections_from_spline` | Generate detections from spline-interpolated tracks |
| `SENSOR_PROFILES`, `EMITTER_PROFILES`  | Define sensor and emitter characteristics |
| `compute_bearing`, `offset_position`   | Geographic math utilities |
| `load_geojson`, `plot_geojson_file`    | Load and visualize GeoJSON regions |
| `mask_elint_by_geojson`                | Filter detections within polygons |
| `add_ais_tracks`, `add_spline`         | Visualize AIS tracks and splines |
| `add_elint_detections`                 | Plot detections and error ellipses |
| `init_map`                             | Initialize a Plotly Mapbox map view |

---

## 🚀 Quickstart Example

```python
from elintgen import (
    generate_elint_detections_from_spline,
    SENSOR_PROFILES,
    EMITTER_PROFILES
)
import pandas as pd

track_df = pd.read_csv("example_track.csv")  # Must include Timestamp, Latitude, Longitude, TrackID

elint_df, lat_spline, lon_spline = generate_elint_detections_from_spline(
    track_df,
    sensor_type="shore",
    emitter_type="military",
    sensor_profiles=SENSOR_PROFILES,
    emitter_profiles=EMITTER_PROFILES
)
```

## 📊 Visualization Example

```python
from elintgen import init_map, add_ais_tracks, add_elint_detections

fig = init_map()
fig = add_ais_tracks(track_df, fig=fig)
fig = add_elint_detections(elint_df, fig=fig)
fig.show()
```

# 🔬 Scenario Complexity Framework

`ELINTgen` supports complex, realistic environments for testing fusion and tracking systems. You can define scenarios in YAML that apply one or more complexity modules to AIS or ELINT data.

## 🔧 Complexity Modules

Each module introduces a type of realism, ambiguity, or degradation in the data.

### 🛰 Goal 1: Co-travel / Overlapping Tracks

| ID                 | Description                                      |
|--------------------|--------------------------------------------------|
| `parallel_tracks`  | Adds a nearby vessel with similar heading/speed |
| `merge_split_tracks` | Splits or merges vessels mid-track             |
| `shadow_track`     | Creates a lagged copy of another track          |

### 🆔 Goal 2: Identifier Inconsistency

| ID             | Description                                |
|----------------|--------------------------------------------|
| `missing_ids`  | Removes MMSI, name, or call sign fields    |
| `typo_ids`     | Introduces character-level typos           |
| `reused_ids`   | Assigns new ID to vessels   |

### ⏱ Goal 3: Varying Data Quality

| ID                     | Description                                      |
|------------------------|--------------------------------------------------|
| `sensor_lag`           | Adds random lag to detection timestamps          |
| `timestamp_quantization` | Rounds detection times to fixed intervals     |
| `reporting_gaps`       | Removes detections within a defined region       |


