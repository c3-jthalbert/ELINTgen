import pandas as pd
import numpy as np
from .complexity_base import ComplexityModule

class MissingIDs(ComplexityModule):
    def __init__(self, params):
        super().__init__(params)
        self.fields = self.params.get("fields", [])
        self.keep_probability = self.params.get("keep_probability", 1.0)
        self.target_ids = self.params.get("track_ids", None)  # required to do anything

    def apply(self, tracks_df, sensors=None, emitters=None):
        if not self.fields or not self.target_ids:
            return pd.DataFrame(columns=tracks_df.columns)  # no-op if not configured

        tracks_df = tracks_df.copy()
        modified_tracks = []

        for tid, group in tracks_df.groupby("TrackID"):
            if str(tid) not in self.target_ids:
                continue

            group = group.copy()
            for field in self.fields:
                if field in group.columns:
                    mask = np.random.rand(len(group)) > self.keep_probability
                    group.loc[mask, field] = None

            modified_tracks.append(group)

        if modified_tracks:
            return pd.concat(modified_tracks, ignore_index=True)
        else:
            return pd.DataFrame(columns=tracks_df.columns)

