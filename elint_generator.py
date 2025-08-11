import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from .geom_utils import compute_bearing, offset_position


def generate_elint_detections_from_spline(track_df, 
                                          sensor_type, 
                                          emitter_type=None, 
                                          sensor_profiles=None, 
                                          emitter_profiles=None, 
                                          detector_id=0,
                                          error_scale=1.0,           
                                          emitter_field="emitter_profile",  
                                          emitter_fallback="nav_radar_x_band"):
    """
    Generate synthetic ELINT detections along a given AIS track using a cubic spline interpolator.

    Parameters
    ----------
    track_df : pd.DataFrame
        AIS track data with at least columns:
        ['TrackID', 'Timestamp', 'Longitude', 'Latitude'].
        Optionally includes emitter_field for automatic emitter resolution.
    sensor_type : str
        Key into sensor_profiles.
    emitter_type : str, optional
        Key into emitter_profiles. If None, will attempt to resolve from track_df[emitter_field].
    sensor_profiles : dict
        Dictionary of sensor profile definitions.
    emitter_profiles : dict
        Dictionary of emitter profile definitions.
    detector_id : int, default 0
        Numerical ID appended to detector string.
    error_scale : float, default 1.0
        Global scale factor applied to all error ellipse axes (km).
    emitter_field : str, default "emitter_profile"
        Column in track_df to use for emitter auto-resolution.
    emitter_fallback : str, default "nav_radar_x_band"
        Fallback emitter profile if emitter_field is missing.

    Returns
    -------
    elint_df : pd.DataFrame
        Generated ELINT detections.
    lat_spline, lon_spline : CubicSpline
        Splines for latitude and longitude over time.
    """

    # Sort by TrackID + Timestamp to ensure temporal order
    track_df = track_df.sort_values(by=["TrackID", "Timestamp"])

    # Load sensor profile
    if sensor_profiles is None or sensor_type not in sensor_profiles:
        raise ValueError(f"Sensor profile '{sensor_type}' not found.")
    sensor = sensor_profiles[sensor_type]

    # --- Resolve emitter_type from track_df if not given ---
    if emitter_type is None:
        if emitter_field in track_df.columns:
            em = track_df[emitter_field].iloc[0]
            emitter_type = em[0] if isinstance(em, (list, tuple)) else em
        else:
            emitter_type = emitter_fallback

    # Load emitter profile
    if emitter_profiles is None or emitter_type not in emitter_profiles:
        raise ValueError(f"Emitter profile '{emitter_type}' not found.")
    emitter = emitter_profiles[emitter_type]

    # Apply global error scale to sensor's position error
    pos_error_major, pos_error_minor = sensor['pos_error_km']
    pos_error_major *= float(error_scale)
    pos_error_minor *= float(error_scale)

    error_bias = sensor['error_bias']
    detector_loc = sensor.get('detector_location', None)

    elint_records = []

    # Ensure Timestamp is datetime
    track_df['Timestamp'] = pd.to_datetime(track_df['Timestamp'])

    # Drop duplicate timestamps (can break spline interpolation)
    duplicated_mask = track_df['Timestamp'].duplicated(keep='first')
    if duplicated_mask.any():
        print(f"Found repeated timestamps at indices: {np.where(duplicated_mask)[0]}")
        track_df = track_df[~duplicated_mask].reset_index(drop=True)
        print(f"Dropped {duplicated_mask.sum()} duplicate timestamps.")

    # Convert times to POSIX seconds
    times = track_df['Timestamp'].astype(np.int64).values / 1e9
    latitudes = track_df['Latitude'].values
    longitudes = track_df['Longitude'].values

    # Check monotonicity of timestamps
    if not np.all(np.diff(times) > 0):
        print("Warning: times aren't strictly increasing")
        print(np.diff(times))

    # Fit cubic splines to lat/lon over time
    lat_spline = CubicSpline(times, latitudes)
    lon_spline = CubicSpline(times, longitudes)

    # Determine sampling times
    start_time = times[0]
    end_time = times[-1]
    duration_minutes = (end_time - start_time) / 60
    n_samples = int(duration_minutes * sensor['sample_rate_per_min'] * 1.5)
    sample_times = np.linspace(start_time, end_time, n_samples)
    sample_timestamps = pd.to_datetime(sample_times, unit='s')

    # Generate detections
    for timestamp in sample_timestamps:
        lat = lat_spline(timestamp.timestamp())
        lon = lon_spline(timestamp.timestamp())

        # Random chance to skip sample based on rate (1 per minute = 1.0)
        if np.random.rand() > sensor['sample_rate_per_min']:
            continue

        # Probability of emitter being active
        emit_prob = emitter['emission_prob'](timestamp) if callable(emitter['emission_prob']) else emitter['emission_prob']
        if np.random.rand() > emit_prob:
            continue

        # Pick frequency band and power
        band = np.random.choice(emitter['bands'])
        power = np.random.uniform(*emitter['power_range_dbm'])

        # Determine bias angle for error ellipse
        if error_bias == 'random':
            angle_deg = np.random.uniform(0, 360)
        elif error_bias == 'random_small':
            angle_deg = np.random.normal(0, 10)
        elif error_bias == 'bearing_dominant' and detector_loc:
            angle_deg = compute_bearing(detector_loc[0], detector_loc[1], lat, lon) % 360
        else:
            angle_deg = 0

        # Apply position error with rotation
        theta = np.random.uniform(0, 2 * np.pi)
        dx = pos_error_major * np.cos(theta)
        dy = pos_error_minor * np.sin(theta)
        angle_rad = np.radians(angle_deg)
        dx_rot = dx * np.cos(angle_rad) - dy * np.sin(angle_rad)
        dy_rot = dx * np.sin(angle_rad) + dy * np.cos(angle_rad)
        det_lat, det_lon = offset_position(lat, lon, dx_rot, dy_rot)

        # Append record
        elint_records.append({
            'detector_id': f"{sensor_type}_{detector_id}",
            'TrackID': track_df['TrackID'].iloc[0],
            'detection_time': timestamp,
            'true_lat': lat,
            'true_lon': lon,
            'detected_lat': det_lat,
            'detected_lon': det_lon,
            'sensor_type': sensor_type,
            'emitter_type': emitter_type,
            'frequency_band': band,
            'power_dbm': power,
            'error_major_km': pos_error_major,
            'error_minor_km': pos_error_minor,
            'error_angle_deg': angle_deg
        })

    return pd.DataFrame(elint_records), lat_spline, lon_spline

def generate_elint_for_all_emitters(track_df,
                                    sensor_type,
                                    sensor_profiles,
                                    emitter_profiles,
                                    error_scale=1.0,
                                    emitter_field="emitter_profile",
                                    emitter_fallback="nav_radar_x_band",
                                    detector_id=0):
    """
    Generate a separate ELINT DataFrame for each emitter type in the track's emitter_field.
    Returns a list of DataFrames, one per emitter.
    """
    # Resolve list of emitters for this track
    if emitter_field in track_df.columns:
        em = track_df[emitter_field].iloc[0]
        emitter_list = list(em) if isinstance(em, (list, tuple)) else [em]
    else:
        emitter_list = [emitter_fallback]

    elint_dfs = []
    for i, emitter_type in enumerate(emitter_list):
        df_elint, _, _ = generate_elint_detections_from_spline(
            track_df=track_df,
            sensor_type=sensor_type,
            emitter_type=emitter_type,
            sensor_profiles=sensor_profiles,
            emitter_profiles=emitter_profiles,
            detector_id=f"{detector_id}_{i}",
            error_scale=error_scale
        )
        elint_dfs.append(df_elint)

    return elint_dfs
