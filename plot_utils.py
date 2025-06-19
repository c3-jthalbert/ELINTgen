import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def add_ais_tracks(df, fig=None, color="TrackID", hover="Timestamp"):
    """
    Add AIS vessel tracks as colored polylines to a Plotly map.

    Parameters:
        df (pd.DataFrame): Must have 'Latitude', 'Longitude', 'TrackID', 'Timestamp'
        fig (plotly.graph_objs.Figure): Optional existing figure to add to
        color (str): Column to color by (default 'TrackID')
        hover (str or list): Column(s) to show in hover info

    Returns:
        fig (plotly.graph_objs.Figure)
    """
    df_sorted = df.sort_values(by=["TrackID", "Timestamp"])
    base_fig = px.line_map(
        df_sorted,
        lat="Latitude",
        lon="Longitude",
        color=color,
        line_group="TrackID",
        hover_data=hover if isinstance(hover, list) else [hover],
        height=600,
        zoom=5
    )
    if fig is None:
        return base_fig
    for trace in base_fig.data:
        fig.add_trace(trace)
    return fig

import numpy as np
import pandas as pd
import plotly.express as px

def add_spline(lat_spline, lon_spline, t_range=None, fig=None, color="red", name="Spline", n=200):
    """
    Add a spline path to a map using px.line_map.

    Parameters:
        lat_spline, lon_spline: Callable functions of time
        t_range (tuple or None): (start_time, end_time) in seconds since epoch. 
                                 If None, uses full spline domain.
        fig: Optional existing Plotly map figure
        color: Line color
        name: Legend label
        n: Number of interpolation points

    Returns:
        fig: Updated Plotly figure
    """
    if t_range is None:
        t_range = (lat_spline.x[0], lat_spline.x[-1])

    t_vals = np.linspace(t_range[0], t_range[1], n)
    lat_vals = lat_spline(t_vals)
    lon_vals = lon_spline(t_vals)

    spline_df = pd.DataFrame({
        "lat": lat_vals,
        "lon": lon_vals,
        "group": name
    })

    overlay = px.line_map(
        spline_df,
        lat="lat",
        lon="lon",
        line_group="group",
    )
    overlay.update_traces(line=dict(color=color), name=name, showlegend=True)

    if fig is None:
        return overlay

    for trace in overlay.data:
        fig.add_trace(trace)

    return fig


def generate_ellipse_points(lat, lon, major_km, minor_km, angle_deg, n_points=36):
    angles = np.linspace(0, 2 * np.pi, n_points)
    x = major_km * np.cos(angles)
    y = minor_km * np.sin(angles)

    angle_rad = np.radians(angle_deg)
    x_rot = x * np.cos(angle_rad) - y * np.sin(angle_rad)
    y_rot = x * np.sin(angle_rad) + y * np.cos(angle_rad)

    lat_offset = lat + (y_rot / 111.0)
    lon_offset = lon + (x_rot / (111.320 * np.cos(np.radians(lat))))
    return lat_offset, lon_offset

def add_elint_detections(df, fig=None, color="orange", ellipse_color="red", opacity=0.3, name="ELINT"):
    """
    Add ELINT detection points and error ellipses to a Plotly maplibre map.

    Parameters:
        df (pd.DataFrame): ELINT detections with fields including detected_lat, detected_lon, error info
        fig (go.Figure): Optional existing Plotly figure to add to
        color (str): Color for detection points
        ellipse_color (str): Color for error ellipses
        opacity (float): Opacity for error ellipses
        name (str): Label for legend

    Returns:
        fig (go.Figure)
    """
    if df.empty:
        print("Warning: ELINT DataFrame is empty.")
        return fig

    df = df.copy()
    df["label"] = name

    scatter = px.scatter_map(
        df,
        lat="detected_lat",
        lon="detected_lon",
        color_discrete_sequence=[color],
        hover_name="detection_time",
        hover_data=["frequency_band", "power_dbm", "sensor_type", "emitter_type"],
    )
    scatter.update_traces(marker=dict(size=6), name=name, showlegend=True)

    if fig is None:
        fig = scatter
    else:
        for trace in scatter.data:
            fig.add_trace(trace)

    # Add ellipses using px.line_map
    ellipse_traces = []
    for _, row in df.iterrows():
        lat_pts, lon_pts = generate_ellipse_points(
            row["detected_lat"],
            row["detected_lon"],
            row["error_major_km"],
            row["error_minor_km"],
            row["error_angle_deg"]
        )
        lat_pts = np.append(lat_pts, lat_pts[0])
        lon_pts = np.append(lon_pts, lon_pts[0])
        ellipse_df = pd.DataFrame({'lat': lat_pts, 'lon': lon_pts})

        ellipse_fig = px.line_map(
            ellipse_df,
            lat="lat",
            lon="lon"
        )
        ellipse_fig.update_traces(
            line=dict(width=0),
            fill="toself",
            fillcolor=f"rgba(255,0,0,{opacity})",
            hoverinfo='skip',
            showlegend=False
        )
        ellipse_traces.extend(ellipse_fig.data)

    for trace in ellipse_traces:
        fig.add_trace(trace)

    return fig

def init_map(center_lat=23.0, center_lon=120.0, zoom=6):
    """Create a base map figure."""
    return go.Figure().update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(center={"lat": center_lat, "lon": center_lon}, zoom=zoom),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
