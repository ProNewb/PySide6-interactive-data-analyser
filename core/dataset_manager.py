from dataclasses import dataclass

import pandas as pd

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
        self.result_operation_log = []
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
        self.result_operation_log.clear()

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
        self.result_operation_log.append(description)
    def clear_result(self):
        """Remove the current result dataset and its history."""

        self.result_dataframe = None
        self.result_history.clear()
        self.result_redo_history.clear()
        self.result_operation_log.clear()

    def close_file(self):
        """Clear the loaded dataset and all associated project state."""

        had_data = self.dataframe is not None

        self.dataframe = None
        self.original_dataframe = None
        self.history.clear()
        self.redo_history.clear()
        self.operation_log.clear()
        self.clear_result()
        self.result_redo_history.clear()
        self.filename = None

        return had_data

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

    @staticmethod
    def _state_payload(operation, dataframe_to_json):
        return {
            "before": dataframe_to_json(operation.before),
            "after": dataframe_to_json(operation.after),
            "description": operation.description
        }

    @staticmethod
    def _state_from_payload(payload, dataframe_from_json):
        return DataState(
            before=dataframe_from_json(payload["before"]),
            after=dataframe_from_json(payload["after"]),
            description=payload["description"]
        )

    def get_history_snapshot(self, target="main", dataframe_to_json=None):
        """Return capped undo/redo snapshots for project restoration.

        The operation log remains complete; these snapshots are only the
        bounded state needed to keep the five-step undo/redo feature usable
        after reopening a project.
        """
        history = self.history if target == "main" else self.result_history
        redo_history = (
            self.redo_history if target == "main"
            else self.result_redo_history
        )
        return {
            "undo": [
                self._state_payload(operation, dataframe_to_json)
                for operation in history[-self.MAX_HISTORY:]
            ],
            "redo": [
                self._state_payload(operation, dataframe_to_json)
                for operation in redo_history[-self.MAX_HISTORY:]
            ]
        }

    def load_project(
        self,
        filename,
        original,
        current,
        operations,
        result_dataframe=None,
        result_operations=None,
        main_history=None,
        result_history=None,
        dataframe_from_json=None
    ):
        self.filename = filename
        self.original_dataframe = original.copy()
        self.dataframe = current.copy()
        self.operation_log = list(operations or [])
        self.history.clear()
        self.redo_history.clear()

        if dataframe_from_json is None:
            dataframe_from_json = lambda value: value

        main_history = main_history or {}
        self.history = [
            self._state_from_payload(payload, dataframe_from_json)
            for payload in main_history.get("undo", [])[-self.MAX_HISTORY:]
        ]
        self.redo_history = [
            self._state_from_payload(payload, dataframe_from_json)
            for payload in main_history.get("redo", [])[-self.MAX_HISTORY:]
        ]

        self.result_dataframe = (
            None if result_dataframe is None else result_dataframe.copy()
        )
        self.result_operation_log = list(result_operations or [])
        self.result_history = []
        self.result_redo_history = []

        result_history = result_history or {}
        self.result_history = [
            self._state_from_payload(payload, dataframe_from_json)
            for payload in result_history.get("undo", [])[-self.MAX_HISTORY:]
        ]
        self.result_redo_history = [
            self._state_from_payload(payload, dataframe_from_json)
            for payload in result_history.get("redo", [])[-self.MAX_HISTORY:]
        ]

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

    def get_result_operation_log(self):

        return list(self.result_operation_log)

    def numeric_columns(self, dataframe):
        return [
            column
            for column in dataframe.columns
            if (
                pd.api.types.is_numeric_dtype(dataframe[column])
                and not pd.api.types.is_bool_dtype(dataframe[column])
            )
        ]

    def text_columns(self, dataframe):
        return [
            column
            for column in dataframe.columns
            if not pd.api.types.is_numeric_dtype(dataframe[column])
            and not pd.api.types.is_datetime64_any_dtype(dataframe[column])
            and (
                pd.api.types.is_object_dtype(dataframe[column])
                or pd.api.types.is_string_dtype(dataframe[column])
                or isinstance(dataframe[column].dtype, pd.CategoricalDtype)
            )
        ]

    def date_columns(self, dataframe):
        return [
            column
            for column in dataframe.columns
            if (
                pd.api.types.is_datetime64_any_dtype(dataframe[column])
                or pd.api.types.is_datetime64_dtype(dataframe[column])
            )
        ]