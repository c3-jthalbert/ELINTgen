# profiles.py

"""
Sensor and Emitter Profile Definitions for ELINT Simulation
"""
# ---- helper utilities (optional, safe to keep at top of profiles.py) ----
def day_night_prob(t, day_p=0.6, night_p=0.25, start=6, end=20):
    """Higher probability during local daytime hours."""
    return day_p if start <= t.hour < end else night_p

def bursty(base=0.4, burst=0.85, period_hours=3):
    """
    Returns a callable emission probability that 'bursts' every period_hours.
    Keeps behavior deterministic from timestamp without global state.
    """
    def _p(t):
        return burst if (t.hour % period_hours) == 0 else base
    return _p

def weekday_peak(t, weekday_p=0.6, weekend_p=0.35):
    """Slightly higher probability on weekdays (port ops, traffic)."""
    return weekday_p if t.weekday() < 5 else weekend_p
# -------------------------------------------------------------------------


EMITTER_PROFILES = {
    # --- Maritime: safety & navigation -----------------------------------
    "ais_class_a": {
        "emission_prob": 0.9,                     # periodic, near-continuous when powered
        "power_range_dbm": [33, 38],              # ~2–6 W VHF effective radiated power
        "bands": ["AIS", "VHF"],
        "category": "radio",
        "domain": "maritime",
        "notes": "SOLAS-class vessels: AIS Class A transponders (position reports at 2–10 s while underway)."
    },
    "ais_class_b": {
        "emission_prob": 0.7,
        "power_range_dbm": [27, 33],              # ~0.5–2 W
        "bands": ["AIS", "VHF"],
        "category": "radio",
        "domain": "maritime",
        "notes": "Smaller craft: AIS Class B/SO. Lower duty and power than Class A."
    },
    "vhf_marine_bridge": {
        "emission_prob": lambda t: day_night_prob(t, 0.55, 0.25),
        "power_range_dbm": [33, 40],              # handheld to fixed set
        "bands": ["VHF"],
        "category": "radio",
        "domain": "maritime",
        "emission_pattern": "short voice calls, DSC bursts",
        "duty_cycle": "intermittent",
        "notes": "Ch. 13/16 bridge-to-bridge, harbor ops; heavier in daylight."
    },

    # --- Maritime: navigation radars (commercial) ------------------------
    "nav_radar_x_band": {
        "emission_prob": lambda t: weekday_peak(t, 0.7, 0.5),
        "power_range_dbm": [60, 85],              # peak tx power (pulsed magnetron/solid-state)
        "bands": ["X"],
        "category": "radar",
        "domain": "maritime",
        "scan_mode": "surface search",
        "pri": "short-medium",
        "notes": "Common 9–10 GHz shipboard nav radar; continuous while underway/at anchor watch."
    },
    "nav_radar_s_band": {
        "emission_prob": lambda t: weekday_peak(t, 0.55, 0.35),
        "power_range_dbm": [65, 90],
        "bands": ["S"],
        "category": "radar",
        "domain": "maritime",
        "scan_mode": "long-range/poor-weather",
        "pri": "medium",
        "notes": "3 GHz class radar used in rain/sea clutter; lower update rate than X-band."
    },

    # --- Maritime: port & coastal infrastructure -------------------------
    "port_vts": {
        "emission_prob": 0.75,
        "power_range_dbm": [40, 60],              # high ERP coastal sites
        "bands": ["VHF", "UHF"],
        "category": "radio",
        "domain": "shore",
        "emission_pattern": "control net + DSC",
        "duty_cycle": "frequent",
        "notes": "Vessel Traffic Service nets near harbors and straits."
    },
    "coastal_surface_search": {
        "emission_prob": 0.85,
        "power_range_dbm": [70, 100],
        "bands": ["X", "S"],
        "category": "radar",
        "domain": "shore",
        "scan_mode": "sector/360°",
        "notes": "Shore-based surface search radar; persistent coastal coverage."
    },

    # --- Maritime: commercial satcom -------------------------------------
    "satcom_maritime_c_ku": {
        "emission_prob": lambda t: day_night_prob(t, 0.55, 0.45),  # fairly steady
        "power_range_dbm": [20, 40],
        "bands": ["C", "Ku"],
        "category": "radio",
        "domain": "maritime",
        "emission_pattern": "packet/data sessions",
        "duty_cycle": "intermittent",
        "notes": "Fleet broadband/IP backhaul; bursty sessions with moderate power."
    },

    # --- Maritime: specialized shipborne sensors (optional) --------------
    "arpa_tracking_uplink": {
        "emission_prob": 0.15,
        "power_range_dbm": [10, 20],
        "bands": ["L"],
        "category": "data",
        "domain": "maritime",
        "emission_pattern": "short bursts",
        "notes": "Low-duty maintenance/status uplinks from ARPA/ECDIS or weather sensors."
    },
    
    "fishing_sonar": {
        "emission_prob": 0.6,                 # often active while working the grounds
        "power_range_dbm": [20, 40],          # abstract units in this sim
        "bands": ["Acoustic-50kHz", "Acoustic-120kHz"],
        "category": "sonar",
        "domain": "maritime",
        "emission_pattern": "pulsed sweeps while trawling/looking",
        "notes": "Hull-mounted fishing sonar for fish-school detection."
    },
    
    "echo_sounder": {
        "emission_prob": 0.85,                # typically left on continuously
        "power_range_dbm": [15, 35],
        "bands": ["Acoustic-50kHz", "Acoustic-200kHz"],
        "category": "sonar",
        "domain": "maritime",
        "emission_pattern": "regular depth pings",
        "notes": "Single/dual-frequency depth sounder for bottom tracking."
    },

    # --- Military naval sets (coarse, safe abstractions) -----------------
    "surface_search_naval": {
        "emission_prob": lambda t: bursty(base=0.5, burst=0.85, period_hours=4)(t),
        "power_range_dbm": [75, 105],
        "bands": ["S", "X"],
        "category": "radar",
        "domain": "maritime",
        "scan_mode": "surface/air navigation",
        "notes": "Generic naval surface-search set; higher burst probability on patrol cycles."
    },
    "naval_fire_control": {
        "emission_prob": 0.25,                   # mostly silent; spikes during drills
        "power_range_dbm": [80, 110],
        "bands": ["X", "Ku"],
        "category": "radar",
        "domain": "maritime",
        "emission_pattern": "short, high-density tracks",
        "duty_cycle": "sporadic",
        "notes": "Abstracted FCR behavior; keep rare to avoid over-spam in sim."
    },

    # --- Air & ground (kept, but refined) --------------------------------
    "tank_radio": {
        "emission_prob": lambda t: bursty(base=0.25, burst=0.6, period_hours=2)(t),
        "power_range_dbm": [20, 40],
        "bands": ["VHF", "UHF"],
        "category": "radio",
        "domain": "ground",
        "equipment": "Generic tank radios",
        "emission_pattern": "voice/data bursts",
        "duty_cycle": "intermittent",
        "notes": "Short-range secure comms; bursts during movement/contact drills."
    },
    "infantry_radio": {
        "emission_prob": lambda t: day_night_prob(t, 0.45, 0.3),
        "power_range_dbm": [15, 35],
        "bands": ["VHF", "UHF"],
        "category": "radio",
        "domain": "ground",
        "equipment": "Generic handheld/manpack",
        "emission_pattern": "voice net + short data",
        "duty_cycle": "intermittent",
        "notes": "Lower power/shorter range; slightly busier in daylight."
    },
    "artillery_radar": {
        "emission_prob": lambda t: bursty(base=0.25, burst=0.7, period_hours=6)(t),
        "power_range_dbm": [55, 85],
        "bands": ["S"],
        "category": "radar",
        "domain": "ground",
        "emission_pattern": "active during fire missions",
        "duty_cycle": "intermittent",
        "notes": "Counter-battery/trajectory tracking; bursty around mission windows."
    },
    "air_defense_radar": {
        "emission_prob": 0.85,
        "power_range_dbm": [75, 105],
        "bands": ["L", "S", "X"],
        "category": "radar",
        "domain": "ground",
        "emission_pattern": "continuous/search + track",
        "duty_cycle": "frequent",
        "notes": "Search/track radars; persistent with occasional high-density tracking."
    },
    "logistics_radio": {
        "emission_prob": lambda t: day_night_prob(t, 0.3, 0.15),
        "power_range_dbm": [12, 28],
        "bands": ["VHF"],
        "category": "radio",
        "domain": "ground",
        "emission_pattern": "convoy voice nets",
        "duty_cycle": "sporadic",
        "notes": "Lower priority traffic; more chatter during daytime convoys."
    },

    # --- Backwards-compat umbrella profiles (optional) -------------------
    "civilian": {
        "emission_prob": 0.2,
        "power_range_dbm": [10, 30],
        "bands": ["AIS", "S-band"],
        "category": "radio",
        "domain": "maritime",
        "notes": "Generic civilian mix (kept for backward compatibility)."
    },
    "military": {
        "emission_prob": 0.7,
        "power_range_dbm": [60, 100],
        "bands": ["X", "Ku", "L"],
        "category": "radar",
        "domain": "maritime",
        "notes": "Generic high-power naval radar (backward compatible)."
    },
    "dual_use": {
        "emission_prob": lambda t: 0.75 if t.hour % 2 == 0 else 0.1,
        "power_range_dbm": [30, 80],
        "bands": ["S", "X", "AIS"],
        "category": "mixed",
        "domain": "maritime",
        "notes": "Variable civilian/military transmission profile (legacy)."
    }
}



SENSOR_PROFILES = {
    # ------- Existing (kept) -------
    "satellite": {
        "sample_rate_per_min": 0.05,    # ~every 20 min
        "pos_error_km": [3.0, 1.0],
        "error_bias": "random",
        "coverage_area": "global",
        "domain": "aerial",
        "notes": "LEO satellite ISR sweep with coarse resolution"
    },
    "shore": {
        "sample_rate_per_min": 0.25,    # every ~4 min
        "pos_error_km": [2.0, 0.3],
        "error_bias": "bearing_dominant",
        "detector_location": (23.565838, 119.609703),
        "max_range_km": 200,
        "coverage_area": "radial",
        "domain": "shore",
        "notes": "Coastal radar or fixed DF array with long-range reach"
    },
    "drone": {
        "sample_rate_per_min": 1.0,
        "pos_error_km": [0.5, 0.2],
        "error_bias": "random_small",
        "coverage_radius_km": 50,
        "coverage_area": "local",
        "domain": "aerial",
        "notes": "Tactical drone-mounted SIGINT sensor"
    },
    "tactical_df_site": {
        "sample_rate_per_min": 0.5,
        "pos_error_km": [1.0, 0.2],
        "error_bias": "bearing_dominant",
        "detector_location": (39.864086, 104.628741),
        "max_range_km": 50,
        "coverage_area": "radial",
        "domain": "ground",
        "notes": "Fixed DF mast near friendly HQ, oriented for battlefield ELINT"
    },
    "mobile_df": {
        "sample_rate_per_min": 1.0,
        "pos_error_km": [0.8, 0.3],
        "error_bias": "random_small",
        "coverage_area": "local",
        "domain": "ground",
        "notes": "JLTV or MRAP-mounted SIGINT with direction-finding capability"
    },
    "rotary_df": {
        "sample_rate_per_min": 2.0,
        "pos_error_km": [0.6, 0.2],
        "error_bias": "random_small",
        "coverage_area": "aerial",
        "domain": "aerial",
        "notes": "UH-60 ISR platform or similar rotary-wing collection asset"
    },

    # ------- Satellites (variants) -------
    "satellite_leo_dense": {
        "sample_rate_per_min": 0.12,     # higher revisit (constellation)
        "pos_error_km": [2.5, 0.9],
        "error_bias": "random",
        "coverage_area": "global",
        "domain": "aerial",
        "notes": "LEO multi-sat pass – better cadence than single-bird LEO"
    },
    "satellite_meo": {
        "sample_rate_per_min": 0.08,
        "pos_error_km": [6.0, 2.5],
        "error_bias": "random",
        "coverage_area": "global",
        "domain": "aerial",
        "notes": "MEO RF collector – wider swath, coarser geoloc"
    },

    # ------- Shore / coastal RF -------
    "shore_highres_xband": {
        "sample_rate_per_min": 0.35,
        "pos_error_km": [1.2, 0.2],
        "error_bias": "bearing_dominant",
        "detector_location": (23.565838, 119.609703),
        "max_range_km": 60,
        "coverage_area": "radial",
        "domain": "shore",
        "notes": "High-resolution coastal radar/DF; short range, tighter ellipses"
    },
    "shore_oth_hf": {
        "sample_rate_per_min": 0.10,
        "pos_error_km": [15.0, 5.0],
        "error_bias": "bearing_dominant",
        "detector_location": (23.565838, 119.609703),
        "max_range_km": 1500,
        "coverage_area": "radial",
        "domain": "shore",
        "notes": "Over‑the‑horizon HF DF/radar abstraction; huge reach, coarse position"
    },

    # ------- Airborne (fixed-wing ISR) -------
    "fixedwing_widearea": {
        "sample_rate_per_min": 1.5,      # fast sweeps
        "pos_error_km": [1.0, 0.4],
        "error_bias": "random_small",
        "coverage_radius_km": 150,
        "coverage_area": "local",
        "domain": "aerial",
        "notes": "High-altitude ISR (P-8/Global‑type) loiter; strong geoloc"
    },
    "fixedwing_geolocate": {
        "sample_rate_per_min": 1.2,
        "pos_error_km": [0.8, 0.3],
        "error_bias": "random_small",
        "coverage_radius_km": 120,
        "coverage_area": "local",
        "domain": "aerial",
        "notes": "TDOA/FDOA‑style geolocation abstraction; tight ellipses"
    },

    # ------- UAV (variants) -------
    "uav_ha_loiter": {
        "sample_rate_per_min": 1.2,
        "pos_error_km": [0.4, 0.15],
        "error_bias": "random_small",
        "coverage_radius_km": 120,
        "coverage_area": "local",
        "domain": "aerial",
        "notes": "High‑altitude long‑endurance UAV; clean geometry, wide radius"
    },
    "uav_su_tactical": {
        "sample_rate_per_min": 1.0,
        "pos_error_km": [0.6, 0.25],
        "error_bias": "random_small",
        "coverage_radius_km": 30,
        "coverage_area": "local",
        "domain": "aerial",
        "notes": "Small UAS over the AOI; decent cadence, moderate accuracy"
    },

    # ------- Maritime ESM/DF -------
    "ship_esm": {
        "sample_rate_per_min": 0.8,
        "pos_error_km": [2.0, 0.7],
        "error_bias": "random_small",
        "coverage_radius_km": 70,
        "coverage_area": "local",
        "domain": "maritime",
        "notes": "ESM/DF on a vessel; good bearing accuracy, moderate range"
    },

    # ------- Aerostat / tethered tower -------
    "aerostat_df": {
        "sample_rate_per_min": 0.8,
        "pos_error_km": [1.5, 0.6],
        "error_bias": "bearing_dominant",
        "detector_location": (24.200000, 120.300000),
        "max_range_km": 80,
        "coverage_area": "radial",
        "domain": "aerial",
        "notes": "Tethered balloon/tower DF over coast; persistent local coverage"
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