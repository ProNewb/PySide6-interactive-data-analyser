from dataclasses import dataclass

from core.csv_reader import CSVReader
from analysis.data_summary import DataSummary

from dataclasses import dataclass

from core.csv_reader import CSVReader
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QWidget,
    QLabel,
    QVBoxLayout
)

@dataclass
class DataState:

    dataframe: object
    description: str


class DatasetManager:

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
        
    def has_data(self):

        return self.dataframe is not None

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

    # ==================================================
    # RESULT DATASET
    # ==================================================

    def has_result(self):

        return self.result_dataframe is not None

    def get_result_dataframe(self):

        return self.result_dataframe

    def set_result_dataframe(
        self,
        dataframe,
        description="Result changed"
    ):

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

        self.result_dataframe = None
        self.result_history.clear()

    # ==================================================
    # HISTORY
    # ==================================================

    def can_undo(self, target="main"):

        if target == "main":
            return len(self.history) > 0

        return len(self.result_history) > 0

    def undo_operation(self):

        target = self.target_combo.currentData()

        if target == "selection":
            QMessageBox.information(
                self,
                "Undo",
                "Undo cannot be applied directly to a selection."
            )
            return

        description = self.dataset_manager.undo(
            target
        )

        if description is not None:

            self.refresh_views()

            self.status.showMessage(
                f"Undid: {description}"
            )

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

        return True