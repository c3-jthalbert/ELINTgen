from abc import ABC, abstractmethod

class ComplexityModule(ABC):
    """
    Abstract base class for all AIS/ELINT complexity modules.
    """

    def __init__(self, params: dict):
        self.params = params

    def select_target_tracks(self, tracks_df):
        """
        Optionally filter which tracks to apply this module to.
        Override in subclasses or specify 'track_ids' in params.
        """
        track_ids = self.params.get("track_ids", None)
        if track_ids is not None:
            return tracks_df[tracks_df["TrackID"].isin(track_ids)].copy()
        return tracks_df.copy()

    @abstractmethod
    def apply(self, tracks_df, sensors=None, emitters=None):
        """
        Apply the complexity transformation.

        Parameters:
            tracks_df (pd.DataFrame): The full AIS ground truth dataset.
            sensors (dict): Optional sensor config.
            emitters (dict): Optional emitter config.

        Returns:
            pd.DataFrame: Combined DataFrame (original + new or modified rows).
        """
        pass

