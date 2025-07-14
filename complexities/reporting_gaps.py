import pandas as pd
import json
from shapely.geometry import shape, Point
from .complexity_base import ComplexityModule

class ReportingGaps(ComplexityModule):
    def __init__(self, params):
        super().__init__(params)
        self.target_ids = self.params.get("track_ids", None)

        gap_path = self.params.get("gap_region", None)
        if gap_path:
            with open(gap_path, "r") as f:
                geojson = json.load(f)
                self.gap_region = shape(geojson["features"][0]["geometry"])
        else:
            self.gap_region = None


    def apply(self, tracks_df, sensors=None, emitters=None):
        if self.gap_region is None:
            return pd.DataFrame(columns=tracks_df.columns)

        subset = self.select_target_tracks(tracks_df)
        modified_tracks = []

        for tid, group in subset.groupby("TrackID"):
            if str(tid) not in self.target_ids:
                continue

            group = group.copy()

            mask = group.apply(
                lambda row: self.gap_region.contains(Point(row["detected_lon"], row["detected_lat"])),
                axis=1
            )

            group = group[~mask]  # keep only detections outside gap

            if group.empty:
                continue

            group["TrackID"] = f"{tid}_gapped"
            group["ParentTrackID"] = tid
            group["IsSynthetic"] = True
            group["SyntheticType"] = "gapped"
            group["WasGapped"] = True

            modified_tracks.append(group)

        if modified_tracks:
            return pd.concat(modified_tracks, ignore_index=True)
        else:
            return pd.DataFrame(columns=tracks_df.columns)

