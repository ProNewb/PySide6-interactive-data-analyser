import pandas as pd


class DatasetManager:
    """Stores and manages the currently loaded dataset."""

    def __init__(self):
        self.dataframe = None
        self.filename = None


    def load_csv(
        self,
        filename,
        header="infer"
        ):
            self.dataframe = pd.read_csv(
            filename,
            header=header
        )

    def get_dataframe(self):
        """Return the current dataframe."""

        return self.dataframe

    def has_data(self):
        """Return True if a dataset is loaded."""

        return self.dataframe is not None