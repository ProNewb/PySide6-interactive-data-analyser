from dataclasses import dataclass

from core.csv_reader import CSVReader


@dataclass
class DataState:
    """Stores a previous dataset state for undo operations."""

    dataframe: object
    description: str


class DatasetManager:
    """Stores datasets and manages their modification history."""

    MAX_HISTORY = 5

    def __init__(self):

        self.reader = CSVReader()

        # Main dataset
        self.dataframe = None
        self.original_dataframe = None
        self.history = []

        # Result dataset
        self.result_dataframe = None
        self.result_history = []

        self.filename = None

    # ==================================================
    # MAIN DATASET
    # ==================================================

    def load_csv(self, filename, options):
        """Load a new CSV and reset dataset state."""

        self.filename = filename

        self.dataframe = self.reader.read(
            filename,
            options
        )

        if options.manual_headers:
            self.dataframe.columns = options.manual_headers

        self.original_dataframe = self.dataframe.copy()

        # Loading a new dataset starts a new history.
        self.history.clear()

        # Results belong to the previous dataset.
        self.result_dataframe = None
        self.result_history.clear()

    def has_data(self):
        """Return True if a main dataset is loaded."""

        return self.dataframe is not None

    def get_dataframe(self):
        """Return the current main dataset."""

        return self.dataframe

    def set_dataframe(
        self,
        dataframe,
        description="Data changed"
    ):
        """Replace the main dataset and record its previous state."""

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

    # ==================================================
    # RESULT DATASET
    # ==================================================

    def has_result(self):
        """Return True if a result dataset exists."""

        return self.result_dataframe is not None

    def get_result_dataframe(self):
        """Return the current result dataset."""

        return self.result_dataframe

    def set_result_dataframe(
        self,
        dataframe,
        description="Result changed"
    ):
        """Replace the result dataset and record its previous state."""

        if self.result_dataframe is not None:

            self.result_history.append(
                DataState(
                    self.result_dataframe.copy(),
                    description
                )
            )

            if len(self.result_history) > self.MAX_HISTORY:
                self.result_history.pop(0)

        self.result_dataframe = dataframe.copy()

    def clear_result(self):
        """Remove the current result dataset and its history."""

        self.result_dataframe = None
        self.result_history.clear()

    # ==================================================
    # HISTORY
    # ==================================================

    def can_undo(self, target="main"):
        """Return whether the selected dataset has an undo state."""

        if target == "main":
            return len(self.history) > 0

        if target == "result":
            return len(self.result_history) > 0

        return False

    def undo(self, target="main"):
        """Restore the previous state of the selected dataset."""

        if target == "main":
            history = self.history

        elif target == "result":
            history = self.result_history

        else:
            raise ValueError(
                f"Invalid undo target: {target}"
            )

        if not history:
            return None

        previous_state = history.pop()

        if target == "main":
            self.dataframe = previous_state.dataframe.copy()

        else:
            self.result_dataframe = previous_state.dataframe.copy()

        return previous_state.description

    # ==================================================
    # RESET
    # ==================================================

    def can_reset(self):
        """Return whether the main dataset differs from its original state."""

        if self.original_dataframe is None:
            return False

        if self.dataframe is None:
            return False

        return not self.dataframe.equals(
            self.original_dataframe
        )

    def reset(self):
        """Restore the main dataset to its original state."""

        if not self.can_reset():
            return False

        self.dataframe = self.original_dataframe.copy()
        self.history.clear()

        return True