from dataclasses import dataclass, field
import pandas as pd

from core.csv_reader import CSVReader


@dataclass
class DataState:
    before: object
    after: object
    description: str


@dataclass
class ResultDataset:
    name: str
    dataframe: pd.DataFrame

    history: list[DataState] = field(default_factory=list)
    redo: list[DataState] = field(default_factory=list)
    operations: list[str] = field(default_factory=list)


class DatasetManager:

    MAX_HISTORY = 5

    def __init__(self):

        self.reader = CSVReader()

        # ---------- Main ----------
        self.dataframe = None
        self.original_dataframe = None
        self.history = []
        self.redo_history = []
        self.operation_log = []

        # ---------- Results ----------
        self.results: list[ResultDataset] = []
        self.active_result = -1

        self.filename = None

    # ==================================================
    # MAIN DATASET
    # ==================================================

    def get_dataframe(self):
        return self.dataframe

    def has_data(self):
        return self.dataframe is not None
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
        self.redo_history.clear()
        self.operation_log = list(operations or [])

        # Clear previous results
        self.results.clear()
        self.active_result = -1

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
    # RESULT HELPERS
    # ==================================================

    def has_results(self):
        return len(self.results) > 0

    def set_active_result(self, index):

        if 0 <= index < len(self.results):
            self.active_result = index

    def get_active_result(self):

        if not self.has_results():
            return None

        if self.active_result < 0:
            self.active_result = 0

        return self.results[self.active_result]

    # ==================================================
    # RESULT CRUD
    # ==================================================

    def add_result(self, dataframe, name="Result"):

        result = ResultDataset(
            name=name,
            dataframe=dataframe.copy()
        )

        self.results.append(result)

        self.active_result = len(self.results) - 1

        return self.active_result

    def get_result_dataframe(self, index=None):

        if not self.has_results():
            return None

        if index is None:
            result = self.get_active_result()
        else:
            result = self.results[index]

        return result.dataframe

    def get_result_name(self, index=None):

        if not self.has_results():
            return None

        if index is None:
            result = self.get_active_result()
        else:
            result = self.results[index]

        return result.name

    def replace_result(
        self,
        dataframe,
        description="Result changed",
        index=None
    ):

        if index is None:
            result = self.get_active_result()
        else:
            result = self.results[index]

        operation = DataState(
            before=result.dataframe.copy(),
            after=dataframe.copy(),
            description=description
        )

        result.history.append(operation)

        if len(result.history) > self.MAX_HISTORY:
            result.history.pop(0)

        result.redo.clear()

        result.operations.append(description)

        result.dataframe = dataframe.copy()

    def remove_result(self, index):

        if not (0 <= index < len(self.results)):
            return

        self.results.pop(index)

        if not self.results:
            self.active_result = -1
        else:
            self.active_result = min(index, len(self.results) - 1)

    # ==================================================
    # RESULT HISTORY
    # ==================================================

    def can_undo(self, target="main"):

        if target == "main":
            return bool(self.history)

        result = self.get_active_result()
        return result is not None and bool(result.history)

    def can_redo(self, target="main"):

        if target == "main":
            return bool(self.redo_history)

        result = self.get_active_result()
        return result is not None and bool(result.redo)

    def undo(self, target="main"):

        if target == "main":

            if not self.history:
                return None

            operation = self.history.pop()

            self.dataframe = operation.before.copy()

            self.redo_history.append(operation)

            return operation.description

        # Result

        result = self.get_active_result()

        if result is None or not result.history:
            return None

        operation = result.history.pop()

        result.dataframe = operation.before.copy()

        result.redo.append(operation)

        return operation.description

    def redo(self, target="main"):

        if target == "main":

            if not self.redo_history:
                return None

            operation = self.redo_history.pop()

            self.dataframe = operation.after.copy()

            self.history.append(operation)

            return operation.description

        # Result

        result = self.get_active_result()

        if result is None or not result.redo:
            return None

        operation = result.redo.pop()

        result.dataframe = operation.after.copy()

        result.history.append(operation)

        return operation.description

    def get_undo_history(self, target="main"):

        if target == "main":
            return list(self.history)

        result = self.get_active_result()
        return [] if result is None else list(result.history)

    def get_redo_history(self, target="main"):

        if target == "main":
            return list(self.redo_history)

        result = self.get_active_result()
        return [] if result is None else list(result.redo)

    def get_result_operation_log(self):

        result = self.get_active_result()

        return [] if result is None else list(result.operations)

    # ==================================================
    # CLOSE
    # ==================================================

    def close_file(self):

        self.dataframe = None
        self.original_dataframe = None

        self.history.clear()
        self.redo_history.clear()
        self.operation_log.clear()

        self.results.clear()
        self.active_result = -1

        self.filename = None

    # ==================================================
    # RESET
    # ==================================================

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

        self.history.clear()
        self.redo_history.clear()
        self.operation_log.clear()

        return True

    def set_result_dataframe(
        self,
        dataframe,
        description="Result changed"
    ):
        if not self.has_results():

            index = self.add_result(
                dataframe,
                "Result"
            )

            result = self.results[index]
            result.operations.append(description)

            return

        self.replace_result(
            dataframe,
            description
        )

    def has_result(self):
        return self.has_results()