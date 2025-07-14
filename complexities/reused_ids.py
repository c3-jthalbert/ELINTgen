import pandas as pd
import numpy as np
import random
import string
from .complexity_base import ComplexityModule

class ReusedIDs(ComplexityModule):
    def __init__(self, params):
        super().__init__(params)
        self.fields_to_replace = self.params.get("fields_to_replace", [])
        self.target_ids = self.params.get("track_ids", None)

    def generate_random_string(self, length=6):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def apply(self, tracks_df, sensors=None, emitters=None):
        if not self.target_ids:
            return pd.DataFrame(columns=tracks_df.columns)

        tracks_df = tracks_df.copy()
        subset = self.select_target_tracks(tracks_df)
        reused_tracks = []

        for tid, group in subset.groupby("TrackID"):
            group = group.copy()

            # Replace values in selected fields with synthetic ones
            for field in self.fields_to_replace:
                if field in group.columns:
                    group[field] = self.generate_random_string()

            group["TrackID"] = f"{tid}_reused"
            group["ParentTrackID"] = tid
            group["IsSynthetic"] = True
            group["SyntheticType"] = "reused"

            reused_tracks.append(group)

        if reused_tracks:
            return pd.concat(reused_tracks, ignore_index=True)
        return pd.DataFrame(columns=tracks_df.columns)

