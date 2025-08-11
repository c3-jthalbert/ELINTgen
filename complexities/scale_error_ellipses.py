import pandas as pd
import numpy as np
from .complexity_base import ComplexityModule

class ScaleErrorEllipses(ComplexityModule):
    def __init__(self, params):
        super().__init__(params)
        self.scale = self.params.get("error_scale", 1.0)
        self.target_ids = self.params.get("track_ids", None)

    def apply(self, elint_df, **kwargs):
        subset = self.select_target_tracks(elint_df)
        scaled = []

        for tid, group in subset.groupby("TrackID"):
            group = group.copy()
            group["error_major_km"] *= self.scale
            group["error_minor_km"] *= self.scale
            group["SyntheticType"] = "error_scaled"
            group["IsSynthetic"] = True
            group["ParentTrackID"] = tid
            group["TrackID"] = f"{tid}_error{self.scale}"
            scaled.append(group)

        return pd.concat(scaled, ignore_index=True) if scaled else None
