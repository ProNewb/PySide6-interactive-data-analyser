from dataclasses import dataclass, field
import pandas as pd

from core.csv_reader import CSVReader


@dataclass
class DataState:
    before: object
    after: object
    description: str

@dataclass
class DatasetState:
    name: str
    dataframe: pd.DataFrame

    history: list[DataState] = field(default_factory=list)
    redo_history: list[DataState] = field(default_factory=list)
    operations: list[str] = field(default_factory=list)
    

class DatasetManager:

    MAX_HISTORY = 5

    def __init__(self):

        self.reader = CSVReader()

        self.main = DatasetState(
            name="Main",
            dataframe=pd.DataFrame()
        )

        self.original_dataframe = None
        self.results = []
        self.active_result = -1
        self.filename = None

    # ==================================================
    # MAIN DATASET
    # ==================================================
    def state(self, target="main", index=None) -> DatasetState | None:
        if target == "main":
            return self.main

        if not self.results:
            return None

        if index is None:
            index = self.active_result

        return self.results[index]

    def get_state(self, target="main", index=None):
        if target == "main":
            return self.main

        if target == "result":
            if index is None:
                index = self.active_result

            if 0 <= index < len(self.results):
                return self.results[index]

        return None

    def get_dataframe(self):
        return self.main.dataframe

    def has_data(self):
        return not self.main.dataframe.empty
    
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

        self.filename = filename

        self.main.dataframe = dataframe.copy()

        self.original_dataframe = (
            dataframe.copy()
            if original_dataframe is None
            else original_dataframe.copy()
        )

        self.main.history.clear()
        self.main.redo_history.clear()
        self.main.operations = list(operations or [])

        self.results.clear()
        self.active_result = -1



    def set_dataframe(
        self,
        dataframe,
        description="Data changed"
    ):

        state = self.main

        if state.dataframe is not None and not state.dataframe.empty:

            operation = DataState(
                before=state.dataframe.copy(),
                after=dataframe.copy(),
                description=description
            )

            state.history.append(operation)

            if len(state.history) > self.MAX_HISTORY:
                state.history.pop(0)

            state.operations.append(description)

        state.dataframe = dataframe.copy()

        # New operation invalidates redo
        state.redo_history.clear()

    # ==================================================
    # RESULT HELPERS
    # ==================================================



    def set_active_result(self, index):

        if 0 <= index < len(self.results):
            self.active_result = index


    # ==================================================
    # RESULT CRUD
    # ==================================================

    def add_result(
        self,
        dataframe,
        name="Result",
        description=None
    ):

        result = DatasetState(
            name=name,
            dataframe=dataframe.copy()
        )

        if description:
            result.operations.append(description)

        self.results.append(result)
        self.active_result = len(self.results) - 1

        return self.active_result



    def get_history(self, target="main", index=None):

        state = self.get_state(target, index)

        if state is None:
            return []

        return state.history

    def replace_result(
        self,
        dataframe,
        description="Result changed",
        index=None
    ):

        state = self.get_state("result", index)

        if state is None:
            return False

        operation = DataState(
            before=state.dataframe.copy(),
            after=dataframe.copy(),
            description=description
        )

        state.history.append(operation)

        if len(state.history) > self.MAX_HISTORY:
            state.history.pop(0)

        state.redo_history.clear()
        state.operations.append(description)

        state.dataframe = dataframe.copy()

        return True

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
    def can_undo(self, target="main", index=None):

        state = self.get_state(target, index)

        if state is None:
            return False

        return bool(state.history)


    def can_redo(self, target="main", index=None):

        state = self.get_state(target, index)

        if state is None:
            return False

        return bool(state.redo_history)

    def undo(self, target="main", index=None):

        state = self.get_state(target, index)

        if state is None or not state.history:
            return None

        operation = state.history.pop()

        state.dataframe = operation.before.copy()

        state.redo_history.append(operation)

        return operation.description

    def redo(self, target="main", index=None):

        state = self.get_state(target, index)

        if state is None or not state.redo_history:
            return None

        operation = state.redo_history.pop()

        state.dataframe = operation.after.copy()

        state.history.append(operation)

        return operation.description

    def get_undo_history(self, target="main", index=None):

        state = self.get_state(target, index)

        if state is None:
            return []

        return list(state.history)


    def get_redo_history(self, target="main", index=None):

        state = self.get_state(target, index)

        if state is None:
            return []

        return list(state.redo_history)


    # ==================================================
    # CLOSE
    # ==================================================

    def close_file(self):

        self.main = DatasetState(
            name="Main",
            dataframe=pd.DataFrame()
        )

        self.original_dataframe = None

        self.results.clear()
        self.active_result = -1
        self.filename = None

    # ==================================================
    # RESET
    # ==================================================

    def can_reset(self):

        if self.original_dataframe is None:
            return False

        if self.main.dataframe is None:
            return False

        return not self.main.dataframe.equals(
            self.original_dataframe
        )


    def reset(self):

        if not self.can_reset():
            return False

        self.main.dataframe = self.original_dataframe.copy()

        self.main.history.clear()
        self.main.redo_history.clear()
        self.main.operations.clear()

        return True


    def current_result(self):
        if not self.results:
            return None

        if self.active_result < 0:
            self.active_result = 0

        return self.results[self.active_result]


    def result(self, index):
        if 0 <= index < len(self.results):
            return self.results[index]
        return None


    def has_results(self):
        return bool(self.results)

    def update_result(self, dataframe, description="Result changed"):
        result = self.current_result()

        if result is None:
            self.add_result(dataframe, description=description)
            return

        self.replace_result(dataframe, description)

    def get_history_snapshot(self, target="main", index=None, dataframe_to_json=None):

        state = self.get_state(target, index)

        if state is None:
            return None

        if dataframe_to_json is None:
            raise ValueError(
                "dataframe_to_json is required"
            )

        return {
            "history": [
                {
                    "before": dataframe_to_json(operation.before),
                    "after": dataframe_to_json(operation.after),
                    "description": operation.description
                }
                for operation in state.history
            ],
            "redo_history": [
                {
                    "before": dataframe_to_json(operation.before),
                    "after": dataframe_to_json(operation.after),
                    "description": operation.description
                }
                for operation in state.redo_history
            ]
        }

    def load_project(
        self,
        filename,
        original,
        current,
        operations=None,
        main_history=None,
        dataframe_from_json=None
    ):

        self.filename = filename

        # -------------------------
        # Main dataset
        # -------------------------

        if current is None:
            current = pd.DataFrame()

        self.main = DatasetState(
            name="Main",
            dataframe=current.copy(),
            operations=list(operations or [])
        )

        # -------------------------
        # Original dataset
        # -------------------------

        self.original_dataframe = (
            None
            if original is None
            else original.copy()
        )

        # -------------------------
        # History
        # -------------------------

        self.main.history.clear()
        self.main.redo_history.clear()

        if (
            main_history
            and dataframe_from_json is not None
        ):

            for saved in main_history.get(
                "history",
                []
            ):

                self.main.history.append(
                    DataState(
                        before=dataframe_from_json(
                            saved["before"]
                        ),
                        after=dataframe_from_json(
                            saved["after"]
                        ),
                        description=saved.get(
                            "description",
                            "Data changed"
                        )
                    )
                )

            for saved in main_history.get(
                "redo_history",
                []
            ):

                self.main.redo_history.append(
                    DataState(
                        before=dataframe_from_json(
                            saved["before"]
                        ),
                        after=dataframe_from_json(
                            saved["after"]
                        ),
                        description=saved.get(
                            "description",
                            "Data changed"
                        )
                    )
                )

        # -------------------------
        # Results
        # -------------------------

        self.results.clear()
        self.active_result = -1

    def new_dataset(self):
        self.main = DatasetState(
            name="Main",
            dataframe=pd.DataFrame()
        )

        self.original_dataframe = pd.DataFrame()

        self.results.clear()
        self.active_result = None