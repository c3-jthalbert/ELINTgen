import pandas as pd
import numpy as np
from elintgen.geom_utils import offset_position, compute_bearing
from .complexity_base import ComplexityModule

class ParallelTracks(ComplexityModule):
    def __init__(self, params):
        super().__init__(params)
        self.distance_km = self.params.get("distance_km", 0.2)
        self.direction = self.params.get("direction", "port")  # port, starboard, or random
        self.time_range = self.params.get("time_range", None)  # e.g., {"start": "00:05", "end": "00:45"}
        self.target_ids = self.params.get("track_ids", None)

    def apply(self, tracks_df, sensors=None, emitters=None):
        tracks_df = tracks_df.copy()
        subset = self.select_target_tracks(tracks_df)
        clones = []

        for tid, track in subset.groupby("TrackID"):
            if self.target_ids and str(tid) not in self.target_ids:
                continue

            track = track.sort_values("Timestamp").copy()

            # Restrict to time range (relative to track start)
            if self.time_range:
                t0 = track["Timestamp"].min()
                t_start = t0 + pd.to_timedelta(self.time_range.get("start", "0min"))
                t_end = t0 + pd.to_timedelta(self.time_range.get("end", "9999min"))
                track = track[(track["Timestamp"] >= t_start) & (track["Timestamp"] <= t_end)]

            if len(track) < 2:
                continue  # Not enough points to compute bearing

            # Compute bearing between successive points
            lat1 = track["Latitude"].values[:-1]
            lon1 = track["Longitude"].values[:-1]
            lat2 = track["Latitude"].values[1:]
            lon2 = track["Longitude"].values[1:]
            bearings = [
                compute_bearing(lat1[i], lon1[i], lat2[i], lon2[i])
                for i in range(len(lat1))
            ]
            bearings.append(bearings[-1])  # repeat last to match length

            # Adjust bearings based on side
            if self.direction == "random":
                angles = [(b + (90 if np.random.rand() < 0.5 else -90)) % 360 for b in bearings]
            elif self.direction == "starboard":
                angles = [(b + 90) % 360 for b in bearings]
            else:  # default: port
                angles = [(b - 90) % 360 for b in bearings]

            offsets = [
                offset_position(lat, lon,
                                dx_km=self.distance_km * np.cos(np.radians(a)),
                                dy_km=self.distance_km * np.sin(np.radians(a)))
                for lat, lon, a in zip(track["Latitude"], track["Longitude"], angles)
            ]

            lat_out, lon_out = zip(*offsets)
            new_track = track.copy()
            new_track["Latitude"] = lat_out
            new_track["Longitude"] = lon_out
            new_track["TrackID"] = f"{tid}_parallel"
            new_track["ParentTrackID"] = tid
            new_track["IsSynthetic"] = True
            new_track["SyntheticType"] = "parallel"

            clones.append(new_track)

        if clones:
            return pd.concat(clones, ignore_index=True)
        return None

