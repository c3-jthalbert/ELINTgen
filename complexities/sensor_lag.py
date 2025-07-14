import pandas as pd
import numpy as np
from .complexity_base import ComplexityModule

class SensorLag(ComplexityModule):
    def __init__(self, params):
        super().__init__(params)
        self.mean_lag = self.params.get("mean_lag_seconds", 60)
        self.jitter = self.params.get("jitter_seconds", 0)
        self.target_ids = self.params.get("track_ids", None)

    def apply(self, tracks_df, sensors=None, emitters=None):
        subset = self.select_target_tracks(tracks_df)

        modified_tracks = []

        for tid, group in subset.groupby("TrackID"):
            if str(tid) not in self.target_ids:
                continue

            group = group.copy()

            delays = np.random.normal(loc=self.mean_lag, scale=self.jitter, size=len(group))
            group["lag_seconds"] = delays
            group["detection_time"] = group["detection_time"] + pd.to_timedelta(delays, unit="s")
            group["WasLagged"] = True

            group["TrackID"] = f"{tid}_lagged"
            group["ParentTrackID"] = tid
            group["IsSynthetic"] = True
            group["SyntheticType"] = "lagged"

            modified_tracks.append(group)

        if modified_tracks:
            return pd.concat(modified_tracks, ignore_index=True)
        else:
            return pd.DataFrame(columns=tracks_df.columns)

