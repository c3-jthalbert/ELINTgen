# ELINTgen
Synthetic ELINT Generation from Vessel Tracks


`ELINTgen` is a modular simulation toolkit for generating synthetic ELINT detections based on real or simulated vessel tracks (e.g., AIS). It supports multi-sensor, multi-emitter scenarios with configurable error, sampling, and fusion complexity.

---

## ✨ Features

- Cubic spline interpolation of AIS tracks
- Configurable ELINT sensors (satellite, shore, drone, etc.)
- Emission models for different emitter types (civilian, military, dual-use)
- Positional error modeling with bearing-based or random biases
- Plotting utilities for AIS tracks, splines, detections, and error ellipses
- GeoJSON-based masking and region visualization

---

## 🔬 Scenario Complexity Framework (Multi-INT)

ELINTgen now supports the simulation of complex, realistic data environments for testing fusion systems. Scenarios are defined using **YAML configuration files** that specify a base track set, sensor/emitter types, and layered **complexity modules**.

### 🔧 Complexity Modules

Each module represents a realism injector and can be applied individually or in sequence.

#### 🛰 Goal 1: Co-travel / Overlap

| ID | Name | Description |
|----|------|-------------|
| `parallel_tracks` | Creates a nearby vessel with similar heading/speed |
| `merge_split_tracks` | Simulates a single vessel splitting into two or merging |
| `shadow_track` | Creates a lagged copy of another track |

#### 🆔 Goal 2: Identifier Inconsistency

| ID | Name | Description |
|----|------|-------------|
| `missing_ids` | Drops MMSI, vessel name, or type from some records |
| `typo_ids` | Introduces small errors in identifier fields |
| `reused_ids` | Assigns the same identifier to different tracks |

#### ⏱ Goal 3: Varying Data Quality

| ID | Name | Description |
|----|------|-------------|
| `sensor_lag` | Adds delay to timestamps for a sensor type |
| `timestamp_quantization` | Rounds timestamps to nearest fixed interval |
| `reporting_gaps` | Drops detections within spatial/temporal zones |

---

## 🧱 YAML Scenario Format
