import pandas as pd
from analysis.data_summary import DataSummary
from core.csv_reader import CSVReader

class DatasetManager:
    """Stores and manages the currently loaded dataset."""






    def has_data(self):
        return self.dataframe is not None
    def __init__(self):
        self.reader = CSVReader()
        self.dataframe = None
        self.original_dataframe = None
        self.filename = None
        self.summary = DataSummary().generate(self.dataframe)

    def load_csv(self, filename, options):

        self.filename = filename

        self.dataframe = self.reader.read(
            filename,
            options
        )

        if options.manual_headers:
            self.dataframe.columns = options.manual_headers

        self.original_dataframe = self.dataframe.copy()

    def get_dataframe(self):
        """Return the current dataframe."""

        return self.dataframe

    def has_data(self):
        """Return True if a dataset is loaded."""

        return self.dataframe is not None

    def set_dataframe(self, dataframe):
        #self.original_dataframe = dataframe.copy()
        self.dataframe = dataframe.copy()

