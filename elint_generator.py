import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from .geom_utils import compute_bearing, offset_position


def generate_elint_detections_from_spline(track_df, sensor_type, emitter_type, sensor_profiles, emitter_profiles, detector_id=0):
    track_df = track_df.sort_values(by=["TrackID", "Timestamp"])
    sensor = sensor_profiles[sensor_type]
    emitter = emitter_profiles[emitter_type]

    sample_rate = sensor['sample_rate_per_min']
    pos_error_major, pos_error_minor = sensor['pos_error_km']
    error_bias = sensor['error_bias']
    detector_loc = sensor.get('detector_location', None)

    elint_records = []

    track_df['Timestamp'] = pd.to_datetime(track_df['Timestamp'])
    duplicated_mask = track_df['Timestamp'].duplicated(keep='first')
    if duplicated_mask.any():
        print(f"Found repeated timestamps at indices: {np.where(duplicated_mask)[0]}")
        track_df = track_df[~duplicated_mask].reset_index(drop=True)
        print(f"Dropped {duplicated_mask.sum()} duplicate timestamps.")

    times = track_df['Timestamp'].astype(np.int64).values / 1e9
    latitudes = track_df['Latitude'].values
    longitudes = track_df['Longitude'].values

    monotone = np.all(np.diff(times) > 0)
    #print(f"times is monotonically increasing: {monotone}")
    if not monotone:
        print("times aren't strictly increasing")
        print(np.diff(times))

    lat_spline = CubicSpline(times, latitudes)
    lon_spline = CubicSpline(times, longitudes)

    start_time = times[0]
    end_time = times[-1]
    duration_minutes = (end_time - start_time) / 60
    n_samples = int(duration_minutes * sample_rate * 1.5)
    sample_times = np.linspace(start_time, end_time, n_samples)
    sample_timestamps = pd.to_datetime(sample_times, unit='s')

    for timestamp in sample_timestamps:
        lat = lat_spline(timestamp.timestamp())
        lon = lon_spline(timestamp.timestamp())

        if np.random.rand() > sample_rate:
            continue

        emit_prob = emitter['emission_prob'](timestamp) if callable(emitter['emission_prob']) else emitter['emission_prob']
        if np.random.rand() > emit_prob:
            continue

        band = np.random.choice(emitter['bands'])
        power = np.random.uniform(*emitter['power_range_dbm'])

        if error_bias == 'random':
            angle_deg = np.random.uniform(0, 360)
        elif error_bias == 'random_small':
            angle_deg = np.random.normal(0, 10)
        elif error_bias == 'bearing_dominant' and detector_loc:
            angle_deg = compute_bearing(detector_loc[0], detector_loc[1], lat, lon) % 360
        else:
            angle_deg = 0

        theta = np.random.uniform(0, 2 * np.pi)
        dx = pos_error_major * np.cos(theta)
        dy = pos_error_minor * np.sin(theta)
        angle_rad = np.radians(angle_deg)
        dx_rot = dx * np.cos(angle_rad) - dy * np.sin(angle_rad)
        dy_rot = dx * np.sin(angle_rad) + dy * np.cos(angle_rad)
        det_lat, det_lon = offset_position(lat, lon, dx_rot, dy_rot)

        elint_records.append({
            'detector_id': f"{sensor_type}_{detector_id}",
            'track_id': track_df['TrackID'].iloc[0],
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
