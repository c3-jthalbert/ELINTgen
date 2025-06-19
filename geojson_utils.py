import json
import pandas as pd
import plotly.express as px
from shapely.geometry import shape, Point, Polygon
import geopandas as gpd

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
