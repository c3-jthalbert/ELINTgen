# ELINTgen: Synthetic ELINT Generation from Vessel Tracks

`ELINTgen` is a lightweight, modular Python toolkit for generating synthetic ELINT detections from real or simulated vessel tracks (e.g., AIS). It supports configurable sensor and emitter profiles, spatial error modeling, and interactive visualization, and is designed for prototyping multi-INT fusion pipelines.

> ⚠️ This code is intended for **research and prototyping purposes only** — not operational use.

---
## Purpose

To support development and demonstration of the fusion pipeline, we implemented a lightweight module that generates synthetic ELINT detections aligned with maritime AIS tracks. This approach is strictly exploratory and intended to scaffold the data story for decision pipelines. It serves to stimulate architectural thinking and system behavior modeling in uncertain, multi-INT environments and is consistent with the contract requirements.

**Code available:** [GitHub - c3-jthalbert/ELINTgen: Synthetic ELINT Generation from Vessel Tracks](https://github.com/c3-jthalbert/ELINTgen)

---

## Approach Summary

### **Input**
- A synthetic or real AIS track, represented as a time-ordered list of `(lat, lon, time)` points.

### **Emitter Profiles**
- Dictionary of emitter types with associated:
  - Frequency bands
  - Power levels
  - Likely radar signatures

### **Sensor Profiles**
- Dictionary of sensor types (e.g., satellite, drone, shore-based) with:
  - Coverage radius
  - Detection error characteristics
  - Biases (e.g., bearing-dominated error for shore radars)

### **Noise Model**
- Configurable stochastic model simulating:
  - Detection dropouts
  - False positives
  - Spurious detections

### **Output**
Each synthetic ELINT detection includes:
- True emitter position (from AIS track)
- Detected position (with injected error)
- Emitter ID and type
- Sensor type that “detected” the emission
- Frequency band and power
- Detection timestamp
- Error ellipse

---

## Code Module Summary: Synthetic ELINT Generation from Vessel Tracks

The module produces synthetic ELINT detections by sampling along a vessel’s AIS track using cubic spline interpolation and injecting detection uncertainty based on sensor and emitter characteristics. It is designed for **scenario simulation and prototype development only**.

---

## Core Logic

### **Track Interpolation**
- AIS track (`lat`, `lon`, `timestamp`) is:
  - Sorted
  - Cleaned of duplicate timestamps
- Cubic splines are fit separately to latitude and longitude over time for smooth interpolation.

### **Sampling Strategy**
- A configurable sample rate (from sensor profile) determines the number of interpolated points.
- Each candidate point is evaluated with:
  - A random filter simulating detection dropout
  - A probabilistic emission test (based on emitter profile logic — constant or time-varying)

### **Error Modeling**
For accepted detections:
- An elliptical positional error is applied.
- Ellipse orientation based on one of:
  - Random heading
  - Small random variation
  - Bearing from a fixed sensor to the true position (`bearing_dominant` mode)
- Resulting offset is computed using a geographic offset function.

### **Output Fields**
Each detection record includes:
- Timestamps (true vs. detected)
- True and detected positions
- Sensor and emitter metadata
- Frequency band and power (from emitter profile)
- Ellipse parameters:
  - Major/minor axis
  - Orientation angle
- Unique `detector_id`

### **Returns**
- `pandas.DataFrame` of detection records
- Spline functions for latitude and longitude (useful for downstream modeling or visualization)

---

## Key Design Notes

- **Not production-grade:** intended for mimicking ELINT behavior when ground truth is unavailable
- **Highly configurable:** sensor/emitter profiles can be adjusted for varied simulation scenarios

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


