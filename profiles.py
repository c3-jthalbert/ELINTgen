# profiles.py

"""
Sensor and Emitter Profile Definitions for ELINT Simulation
"""

# Radar location
radar_lat, radar_lon = 23.565838, 119.609703

EMITTER_PROFILES = {
    "civilian": {
        "emission_prob": 0.2,                  # chance to emit at any time step
        "power_range_dbm": [10, 30],
        "bands": ["AIS", "S-band"]
    },
    "military": {
        "emission_prob": 0.7,
        "power_range_dbm": [60, 100],
        "bands": ["X", "Ku", "L"]
    },
    "dual_use": {
        "emission_prob": lambda t: 0.75 if t.hour % 2 == 0 else 0.1,  # time-sensitive behavior
        "power_range_dbm": [30, 80],
        "bands": ["S", "X", "AIS"]
    }
}

SENSOR_PROFILES = {
    "satellite": {
        "sample_rate_per_min": 0.05,         # ~every 20 min
        "pos_error_km": [3.0, 1.0],            # [major, minor]
        "error_bias": "random",                # isotropic error... could include an orbit path bias
        "coverage_area": "global"
    },
    "shore": {
        "sample_rate_per_min": 0.25,          # every 4 min
        "pos_error_km": [2.0, 0.3],            # bearing-dominant error
        "error_bias": "bearing_dominant",      # major ⟂ to shore-target bearing
        "detector_location": (radar_lat, radar_lon),    # lat/lon of the shore-based sensor
        "max_range_km": 200,                   # max detection range
        "coverage_area": "radial"
    },
    "drone": {
        "sample_rate_per_min": 1.0,            # ~1 per minute
        "pos_error_km": [0.5, 0.2],
        "error_bias": "random_small",
        "coverage_radius_km": 50,              # drone patrol radius
        "coverage_area": "local"
    }
}

def get_sensor_profiles(custom_profiles=None):
    """Return sensor profiles with optional override."""
    if custom_profiles is not None:
        profiles = SENSOR_PROFILES.copy()
        profiles.update(custom_profiles)
        return profiles
    return SENSOR_PROFILES

def get_emitter_profiles(custom_profiles=None):
    """Return emitter profiles with optional override."""
    if custom_profiles is not None:
        profiles = EMITTER_PROFILES.copy()
        profiles.update(custom_profiles)
        return profiles
    return EMITTER_PROFILES