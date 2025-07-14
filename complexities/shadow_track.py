# shadow_track.py

import pandas as pd
from .complexity_base import ComplexityModule

class ShadowTrack(ComplexityModule):
    def __init__(self, params):
        super().__init__(params)
        self.lag_seconds = self.params.get("lag_seconds", 120)

    def apply(self, tracks_df, sensors=None, emitters=None):
        tracks_df = tracks_df.copy()
        subset = self.select_target_tracks(tracks_df)
        clones = []

        for tid, track in subset.groupby("TrackID"):
            track = track.sort_values("Timestamp").copy()
            shadow = track.copy()

            # Apply time lag
            shadow["Timestamp"] = shadow["Timestamp"] + pd.to_timedelta(self.lag_seconds, unit='s')

            # Assign shadow identity and metadata
            shadow["TrackID"] = f"{tid}_shadow"
            shadow["ParentTrackID"] = tid
            shadow["SyntheticType"] = "shadow"
            shadow["IsSynthetic"] = True

            clones.append(shadow)

        if clones:
            return pd.concat(clones, ignore_index=True)
        return None

