from dataclasses import dataclass

from core.csv_reader import CSVReader
from analysis.data_summary import DataSummary


@dataclass
class DataState:

    dataframe: object
    description: str


class DatasetManager:

    MAX_HISTORY = 5

    def __init__(self):

        self.reader = CSVReader()

        self.dataframe = None
        self.original_dataframe = None
        self.filename = None

        self.history = []

    def has_data(self):

        return self.dataframe is not None

    def load_csv(self, filename, options):

        self.filename = filename

        self.dataframe = self.reader.read(
            filename,
            options
        )

        if options.manual_headers:
            self.dataframe.columns = options.manual_headers

        self.original_dataframe = self.dataframe.copy()

        # A newly loaded dataset starts a new history
        self.history.clear()

    def get_dataframe(self):

        return self.dataframe

    def set_dataframe(
        self,
        dataframe,
        description="Data changed"
    ):

        if self.dataframe is not None:

            self.history.append(
                DataState(
                    self.dataframe.copy(),
                    description
                )
            )

            if len(self.history) > self.MAX_HISTORY:
                self.history.pop(0)

        self.dataframe = dataframe.copy()

    def can_undo(self):

        return len(self.history) > 0

    def undo(self):

        if not self.history:
            return None

        previous_state = self.history.pop()

        self.dataframe = previous_state.dataframe.copy()

        return previous_state.description

    def can_reset(self):

        if self.original_dataframe is None:
            return False

        if self.dataframe is None:
            return False

        return not self.dataframe.equals(
            self.original_dataframe
        )

    def reset(self):

        if not self.can_reset():
            return False

        self.dataframe = self.original_dataframe.copy()

        # Reset means we're back at the original state
        self.history.clear()

        return True