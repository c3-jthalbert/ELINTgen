import pandas as pd
import numpy as np
import random
import string
from .complexity_base import ComplexityModule

class TypoIDs(ComplexityModule):
    def __init__(self, params):
        super().__init__(params)
        self.fields = self.params.get("fields", [])
        self.typo_probability = self.params.get("typo_probability", 0.1)
        self.target_ids = self.params.get("track_ids", None)

    def random_typo(self, value):
        if not isinstance(value, str) or len(value) == 0:
            return value
        idx = random.randint(0, len(value) - 1)
        char_pool = string.ascii_letters + string.digits
        new_char = random.choice(char_pool.replace(value[idx], ""))
        return value[:idx] + new_char + value[idx+1:]

    def apply(self, tracks_df, sensors=None, emitters=None):
        subset = self.select_target_tracks(tracks_df)

        modified_tracks = []

        for tid, group in subset.groupby("TrackID"):
            if str(tid) not in self.target_ids:
                continue

            group = group.copy()
            for field in self.fields:
                if field in group.columns:
                    mask = np.random.rand(len(group)) < self.typo_probability
                    group.loc[mask, field] = group.loc[mask, field].apply(self.random_typo)

            group["TrackID"] = f"{tid}_typo"
            group["ParentTrackID"] = tid
            group["IsSynthetic"] = True
            group["SyntheticType"] = "typo"

            modified_tracks.append(group)

        if modified_tracks:
            return pd.concat(modified_tracks, ignore_index=True)
        else:
            return pd.DataFrame(columns=tracks_df.columns)

