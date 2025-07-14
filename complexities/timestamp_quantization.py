import pandas as pd
from .complexity_base import ComplexityModule

class TimestampQuantization(ComplexityModule):
    def __init__(self, params):
        super().__init__(params)
        self.resolution = self.params.get("resolution", "10s")
        self.target_ids = self.params.get("track_ids", None)

    def apply(self, tracks_df, sensors=None, emitters=None):
        subset = self.select_target_tracks(tracks_df)

        modified_tracks = []

        for tid, group in subset.groupby("TrackID"):
            if str(tid) not in self.target_ids:
                continue

            group = group.copy()
            group["detection_time"] = group["detection_time"].dt.round(self.resolution)
            group["WasQuantized"] = True

            group["TrackID"] = f"{tid}_quantized"
            group["ParentTrackID"] = tid
            group["IsSynthetic"] = True
            group["SyntheticType"] = "quantized"

            modified_tracks.append(group)

        if modified_tracks:
            return pd.concat(modified_tracks, ignore_index=True)
        else:
            return pd.DataFrame(columns=tracks_df.columns)

