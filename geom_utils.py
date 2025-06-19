# geometry_utils.py

import numpy as np

def compute_bearing(lat1, lon1, lat2, lon2):
    """
    Compute the bearing in degrees from point (lat1, lon1) to (lat2, lon2).

    Parameters:
        lat1, lon1 (float): Latitude and longitude of the starting point.
        lat2, lon2 (float): Latitude and longitude of the destination point.

    Returns:
        float: Bearing in degrees from North (0-360)
    """
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_lambda = np.radians(lon2 - lon1)
    x = np.sin(delta_lambda) * np.cos(phi2)
    y = np.cos(phi1) * np.sin(phi2) - np.sin(phi1) * np.cos(phi2) * np.cos(delta_lambda)
    return (np.degrees(np.arctan2(x, y)) + 360) % 360

def offset_position(lat, lon, dx_km, dy_km):
    """
    Offset a position in latitude/longitude by a given distance in kilometers.

    Parameters:
        lat, lon (float): Original latitude and longitude.
        dx_km (float): East-west distance to offset in kilometers.
        dy_km (float): North-south distance to offset in kilometers.

    Returns:
        tuple: (new_latitude, new_longitude)
    """
    new_lat = lat + (dy_km / 111.0)
    new_lon = lon + (dx_km / (111.320 * np.cos(np.radians(lat))))
    return new_lat, new_lon
