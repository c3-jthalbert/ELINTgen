import json
import pandas as pd
import plotly.express as px
from shapely.geometry import shape, Point, Polygon
import geopandas as gpd
import numpy as np
from scipy.interpolate import CubicSpline

def load_geojson(filename):
    """Load GeoJSON file and return parsed object."""
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def plot_geojson_file(filename, fig=None, color="blue", zoom=7):
    """Plot GeoJSON polygons on a Plotly map, optionally adding to existing fig."""
    geojson_data = load_geojson(filename)
    features = geojson_data.get("features", [geojson_data] if geojson_data.get("type") == "Feature" else [])

    if not features:
        raise ValueError("No features found in GeoJSON.")

    all_traces = []

    for feature in features:
        geom_type = feature["geometry"]["type"]
        coords = feature["geometry"]["coordinates"]

        if geom_type == "Polygon":
            for ring in coords:
                df = pd.DataFrame(ring, columns=["lon", "lat"])
                trace = px.line_map(df, lat="lat", lon="lon").data[0]
                trace.line.color = color
                all_traces.append(trace)

        elif geom_type == "MultiPolygon":
            for polygon in coords:
                for ring in polygon:
                    df = pd.DataFrame(ring, columns=["lon", "lat"])
                    trace = px.line_map(df, lat="lat", lon="lon").data[0]
                    trace.line.color = color
                    all_traces.append(trace)
        else:
            raise ValueError(f"Unsupported geometry type: {geom_type}")

    if fig is None:
        fig = px.line_map(pd.DataFrame(), lat=[], lon=[])
    
    for trace in all_traces:
        fig.add_trace(trace)

    # Calculate map center
    all_coords = [coord for trace in all_traces for coord in zip(trace.lon, trace.lat)]
    lats, lons = zip(*all_coords)
    lat_center, lon_center = sum(lats)/len(lats), sum(lons)/len(lons)

    fig.update_layout(
        mapbox=dict(center={"lat": lat_center, "lon": lon_center}, zoom=zoom),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    return fig

def plot_geojson_polygon(geojson_data, fig=None, color="blue", zoom=7):
    """
    Plot GeoJSON polygons on a Plotly map, optionally adding to an existing fig.

    Parameters:
        geojson_data (dict): Parsed GeoJSON object
        fig (go.Figure): Optional existing Plotly figure
        color (str): Line color for polygons
        zoom (int): Initial zoom level

    Returns:
        fig (go.Figure): Updated figure
    """
    features = geojson_data.get("features", [geojson_data] if geojson_data.get("type") == "Feature" else [])

    if not features:
        raise ValueError("No features found in GeoJSON.")

    all_traces = []

    for feature in features:
        geom_type = feature["geometry"]["type"]
        coords = feature["geometry"]["coordinates"]

        if geom_type == "Polygon":
            for ring in coords:
                df = pd.DataFrame(ring, columns=["lon", "lat"])
                trace = px.line_map(df, lat="lat", lon="lon").data[0]
                trace.line.color = color
                all_traces.append(trace)

        elif geom_type == "MultiPolygon":
            for polygon in coords:
                for ring in polygon:
                    df = pd.DataFrame(ring, columns=["lon", "lat"])
                    trace = px.line_map(df, lat="lat", lon="lon").data[0]
                    trace.line.color = color
                    all_traces.append(trace)
        else:
            raise ValueError(f"Unsupported geometry type: {geom_type}")

    if fig is None:
        fig = px.line_map(pd.DataFrame(), lat=[], lon=[])

    for trace in all_traces:
        fig.add_trace(trace)

    # Calculate map center
    all_coords = [coord for trace in all_traces for coord in zip(trace.lon, trace.lat)]
    lats, lons = zip(*all_coords)
    lat_center, lon_center = sum(lats)/len(lats), sum(lons)/len(lons)

    fig.update_layout(
        mapbox=dict(center={"lat": lat_center, "lon": lon_center}, zoom=zoom),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    return fig


def mask_elint_by_geojson(elint_df, geojson_file, lat_col="detected_lat", lon_col="detected_lon", invert=False):
    """
    Return a boolean mask indicating whether detections fall inside a GeoJSON polygon.

    Parameters:
        elint_df (DataFrame): The ELINT data
        geojson_file (str or dict): Path to GeoJSON file or already-loaded GeoJSON
        lat_col (str): Column name for latitude
        lon_col (str): Column name for longitude
        invert (bool): If True, returns detections *outside* the polygon

    Returns:
        Series: Boolean mask (True where row is kept)
    """
    if isinstance(geojson_file, str):
        with open(geojson_file, 'r') as f:
            geojson_data = json.load(f)
    else:
        geojson_data = geojson_file

    gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
    combined_shape = gdf.unary_union

    def inside(row):
        return combined_shape.contains(Point(row[lon_col], row[lat_col]))

    mask = elint_df.apply(inside, axis=1)
    return ~mask if invert else mask



def extract_region_subtracks(
    df, region_geojson,
    lat_col="Latitude", lon_col="Longitude", time_col="Timestamp", id_col="mmsi",
    resample_interval_sec=600
):
    """
    Given sparse AIS data, fit a spline to each MMSI track, resample it,
    and extract only the contiguous subtracks fully within a GeoJSON-defined region.

    All original metadata fields are copied into the resampled output where possible.
    """
    region_geom = shape(region_geojson["features"][0]["geometry"])
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.sort_values([id_col, time_col])

    all_subtracks = []
    global_track_counter = 0

    for mmsi, group in df.groupby(id_col):
        group = group.copy()

        if len(group) < 4:
            continue  # not enough points to spline

        t = group[time_col].astype(np.int64) / 1e9  # seconds since epoch
        lat = group[lat_col].values
        lon = group[lon_col].values

        try:
            lat_spline = CubicSpline(t, lat)
            lon_spline = CubicSpline(t, lon)
        except Exception:
            continue  # skip if spline fails

        # Resample timestamps
        t_min, t_max = t.min(), t.max()
        t_resampled = np.arange(t_min, t_max, resample_interval_sec)
        timestamps_resampled = pd.to_datetime(t_resampled, unit='s')
        lat_resampled = lat_spline(t_resampled)
        lon_resampled = lon_spline(t_resampled)

        df_resampled = pd.DataFrame({
            "Timestamp": timestamps_resampled,
            "Latitude": lat_resampled,
            "Longitude": lon_resampled,
            id_col: mmsi
        })

        # Copy static fields from the first row of the original group
        static_data = group.iloc[0].drop([lat_col, lon_col, time_col], errors="ignore")
        for col in static_data.index:
            df_resampled[col] = static_data[col]

        # Point-in-polygon test
        df_resampled["InRegion"] = df_resampled.apply(
            lambda row: region_geom.contains(Point(row["Longitude"], row["Latitude"])),
            axis=1
        )

        # Group by contiguous InRegion blocks
        in_region = df_resampled["InRegion"]
        change_ids = (in_region != in_region.shift()).cumsum()
        for _, segment in df_resampled.groupby(change_ids):
            if segment["InRegion"].all():
                segment = segment.copy()
                segment["TrackID"] = f"{mmsi}_{global_track_counter}"
                global_track_counter += 1
                all_subtracks.append(segment)

    if all_subtracks:
        return pd.concat(all_subtracks, ignore_index=True)
    else:
        return pd.DataFrame(columns=df.columns.tolist() + ["TrackID"])



def coords_to_geojson_polygon(coords, name="GeneratedPolygon"):
    """
    Convert a list of (lon, lat) tuples to a GeoJSON Polygon.
    Assumes the path is closed or will auto-close it.
    """
    if coords[0] != coords[-1]:
        coords.append(coords[0])  # auto-close
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"name": name},
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        }]
    }
