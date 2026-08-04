import pandas as pd
from core.csv_reader import CSVReader

class DatasetManager:
    """Stores and manages the currently loaded dataset."""

    def __init__(self):
        self.reader = CSVReader()
        self.dataframe = None
        self.filename = None


    def load_csv(self, filename, options):

        self.filename = filename

        self.dataframe = self.reader.read(
            filename,
            options
        )

        if options.manual_headers:

            self.dataframe.columns = options.manual_headers

    def get_dataframe(self):
        """Return the current dataframe."""

        return self.dataframe

    def has_data(self):
        """Return True if a dataset is loaded."""

        return self.dataframe is not None