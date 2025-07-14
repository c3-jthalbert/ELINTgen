# merge_split_tracks.py

import numpy as np
import pandas as pd
from elintgen.geom_utils import offset_position
from .complexity_base import ComplexityModule

class MergeSplitTracks(ComplexityModule):
    def __init__(self, params):
        super().__init__(params)
        self.mode = self.params.get("mode", "split")  # "split" or "merge"
        self.offset_bearing = self.params.get("offset_bearing", 15)  # degrees

    def apply(self, tracks_df, sensors=None, emitters=None):
        tracks_df = tracks_df.copy()
        subset = self.select_target_tracks(tracks_df)
        clones = []

        for tid, track in subset.groupby("TrackID"):
            track = track.sort_values("Timestamp").copy()
            n = len(track)
            if n < 4:
                continue

            midpoint_idx = n // 2
            midpoint = track.iloc[midpoint_idx]
            lat0, lon0 = midpoint["Latitude"], midpoint["Longitude"]

            if self.mode == "split":
                new_track = track.copy()
                diverging_part = new_track.iloc[midpoint_idx:].copy()

            elif self.mode == "merge":
                diverging_part = track.iloc[:midpoint_idx].copy()
                new_track = diverging_part.copy()

            else:
                raise ValueError(f"Unsupported mode: {self.mode}")

            # Apply bearing-based rotation around midpoint
            rotated_latlon = []
            for _, row in diverging_part.iterrows():
                dx_km = (row["Longitude"] - lon0) * 111.320 * np.cos(np.radians(lat0))
                dy_km = (row["Latitude"] - lat0) * 111.0

                theta = np.radians(self.offset_bearing)
                dx_rot = dx_km * np.cos(theta) - dy_km * np.sin(theta)
                dy_rot = dx_km * np.sin(theta) + dy_km * np.cos(theta)

                lat_rot = lat0 + dy_rot / 111.0
                lon_rot = lon0 + dx_rot / (111.320 * np.cos(np.radians(lat0)))
                rotated_latlon.append((lat_rot, lon_rot))

            rotated_lat, rotated_lon = zip(*rotated_latlon)

            if self.mode == "split":
                new_track.iloc[midpoint_idx:, new_track.columns.get_loc("Latitude")] = rotated_lat
                new_track.iloc[midpoint_idx:, new_track.columns.get_loc("Longitude")] = rotated_lon
            elif self.mode == "merge":
                new_track["Latitude"] = rotated_lat
                new_track["Longitude"] = rotated_lon

            new_track["TrackID"] = f"{tid}_{self.mode}"
            new_track["SyntheticType"] = self.mode
            new_track["IsSynthetic"] = True
            new_track["ParentTrackID"] = tid

            clones.append(track)
            clones.append(new_track)

        if clones:
            return pd.concat(clones, ignore_index=True)
        return None

