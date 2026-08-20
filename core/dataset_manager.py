from dataclasses import dataclass

from core.csv_reader import CSVReader


@dataclass
class DataState:
    """Stores a previous dataset state for undo operations."""
    before: object
    after: object
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
        self.redo_history = []
        self.operation_log = []

        self.result_dataframe = None
        self.result_history = []
        self.result_redo_history = []

        self.filename = None

    # ==================================================
    # MAIN DATASET
    # ==================================================

    def load_csv(self, filename, options):
        """Load a new CSV and reset dataset state."""

        dataframe = self.reader.read(
            filename,
            options
        )

        if options.manual_headers:
            dataframe.columns = options.manual_headers

        self.load_dataframe(filename, dataframe)

    def load_dataframe(
        self,
        filename,
        dataframe,
        original_dataframe=None,
        operations=None
    ):
        """Load a dataframe and reset or restore its project state."""

        self.filename = filename
        self.dataframe = dataframe.copy()

        self.original_dataframe = (
            dataframe.copy()
            if original_dataframe is None
            else original_dataframe.copy()
        )

        self.history.clear()
        self.operation_log = list(operations or [])

        # Results belong to the previous dataset.
        self.result_dataframe = None
        self.result_history.clear()
        self.result_redo_history.clear()

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

        if self.dataframe is not None:

            self.operation_log.append(description)

            operation = DataState(
                before=self.dataframe.copy(),
                after=dataframe.copy(),
                description=description
            )

            self.history.append(operation)

            if len(self.history) > self.MAX_HISTORY:
                self.history.pop(0)

        self.dataframe = dataframe.copy()

        # A new operation invalidates redo history
        self.redo_history.clear()

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

            operation = DataState(
                before=self.result_dataframe.copy(),
                after=dataframe.copy(),
                description=description
            )

            self.result_history.append(operation)

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
            redo_history = self.redo_history

        elif target == "result":

            history = self.result_history
            redo_history = self.result_redo_history

        else:

            raise ValueError(
                f"Invalid undo target: {target}"
            )

        if not history:
            return None

        operation = history.pop()

        if target == "main":

            self.dataframe = operation.before.copy()

        else:

            self.result_dataframe = operation.before.copy()

        redo_history.append(operation)

        return operation.description

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
        self.operation_log.clear()

        return True

    def get_operation_log(self):
        """Return all operations applied to the main dataframe."""

        return list(self.operation_log)

    def get_undo_history(self):

        return list(self.undo_stack)
    def can_redo(self, target="main"):

        if target == "main":
            return bool(self.redo_history)

        if target == "result":
            return bool(self.result_redo_history)

        return False
    def redo(self, target="main"):

        if target == "main":

            redo_history = self.redo_history
            history = self.history

        elif target == "result":

            redo_history = self.result_redo_history
            history = self.result_history

        else:

            raise ValueError(
                f"Invalid redo target: {target}"
            )

        if not redo_history:
            return None

        operation = redo_history.pop()

        if target == "main":

            self.dataframe = operation.after.copy()

        else:

            self.result_dataframe = operation.after.copy()

        history.append(operation)

        return operation.description
    
    def get_undo_history(self, target="main"):

        if target == "main":
            return list(self.history)

        if target == "result":
            return list(self.result_history)

        return []


    def get_redo_history(self, target="main"):

        if target == "main":
            return list(self.redo_history)

        if target == "result":
            return list(self.result_redo_history)

        return []