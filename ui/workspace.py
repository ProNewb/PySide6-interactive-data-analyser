import json

from io import StringIO

import pandas as pd

from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QInputDialog

from ui.dialogs.import_dialog import ImportDialog
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QSplitter
)

from core.dataset_manager import DatasetManager
from ui.dataset_view import DatasetView
from controllers.file_controller import FileController
from PySide6.QtCore import Qt, QFileInfo

class Workspace(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.dataset_manager = DatasetManager()

        self.file_controller = FileController(
            self.dataset_manager
        )

        self.main_view = DatasetView(
            "Main Dataset"
        )

        self.result_view = DatasetView(
            "Result Dataset"
        )

        self.result_view.hide()

        self.splitter = QSplitter(
            Qt.Horizontal
        )

        self.splitter.addWidget(
            self.main_view
        )

        self.splitter.addWidget(
            self.result_view
        )

        self.splitter.setSizes([
            600,
            600
        ])

        layout = QVBoxLayout(self)

        layout.addWidget(
            self.splitter
        )

        self.refresh()

    # ======================================
    # REFRESH
    # ======================================

    def refresh(self):

        self.update_views()
        self.update_comparison_layout()

    # ======================================
    # VIEWS
    # ======================================

    def update_views(self):

        main = self.dataset_manager.get_dataframe()
        result = self.dataset_manager.get_result_dataframe()

        if main is not None:
            self.main_view.set_dataframe(main)
        else:
            self.main_view.clear()

        if result is not None:
            self.result_view.set_dataframe(result)
        else:
            self.result_view.clear()

        self.update_comparison_layout()

    # ======================================
    # LAYOUT
    # ======================================

    def update_comparison_layout(self):

        main_available = (
            self.dataset_manager.get_dataframe()
            is not None
        )

        result_available = (
            self.dataset_manager.get_result_dataframe()
            is not None
        )

        self.main_view.setVisible(
            main_available
        )

        self.result_view.setVisible(
            result_available
        )

        if main_available and result_available:

            self.splitter.setSizes([
                600,
                600
            ])

        elif main_available:

            self.splitter.setSizes([
                1200,
                0
            ])

        elif result_available:

            self.splitter.setSizes([
                0,
                1200
            ])

    # ==================================================
    # PROJECT AND EXPORT OPERATIONS
    # ==================================================

    def save_project(self):

        project = self.get_project_data()

        if project is None:
            QMessageBox.information(
                None,
                "Save Project",
                "There is no dataset to save."
            )
            return False

        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Save Project",
            "",
            "Project Files (*.json);;All Files (*)"
        )

        if not filename:
            return False

        if not filename.lower().endswith(".json"):
            filename += ".json"

        try:
            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as project_file:

                json.dump(
                    project,
                    project_file,
                    indent=2,
                    default=str
                )

        except OSError as error:

            QMessageBox.warning(
                None,
                "Save Project",
                f"Could not save the project:\n{error}"
            )

            return False

        return True

    def export_csv(self):
        """Export the selected Main or Result dataframe."""

        available = []
        if self.dataset_manager.get_dataframe() is not None:
            available.append(("Main Dataset", "main"))
        if self.dataset_manager.get_result_dataframe() is not None:
            available.append(("Result Dataset", "result"))

        if not available:
            QMessageBox.information(
                None,
                "Export Data",
                "There is no dataset to export."
            )
            return False

        labels = [label for label, _ in available]
        selected_label, accepted = QInputDialog.getItem(
            None,
            "Export Data",
            "Dataset to export:",
            labels,
            0,
            False
        )

        if not accepted:
            return False

        selected_target = dict(available)[selected_label]
        dataframe = (
            self.dataset_manager.get_result_dataframe()
            if selected_target == "result"
            else self.dataset_manager.get_dataframe()
        )

        if dataframe is None:
            QMessageBox.information(
                None,
                "Export Data",
                "There is no dataset to export."
            )
            return False

        filename, selected_filter = QFileDialog.getSaveFileName(
            None,
            "Export Data",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;"
            "JSON Files (*.json);;Parquet Files (*.parquet);;"
            "All Files (*)"
        )

        if not filename:
            return False

        extension = filename.lower().rsplit(".", 1)[-1] \
            if "." in filename else ""

        if not extension:
            extension = {
                "Excel Files (*.xlsx)": "xlsx",
                "JSON Files (*.json)": "json",
                "Parquet Files (*.parquet)": "parquet"
            }.get(selected_filter, "csv")
            filename = f"{filename}.{extension}"

        try:
            if extension == "csv":
                dataframe.to_csv(filename, index=False)
            elif extension in ("xlsx", "xls"):
                dataframe.to_excel(filename, index=False)
            elif extension == "json":
                dataframe.to_json(filename, orient="records", date_format="iso")
            elif extension == "parquet":
                dataframe.to_parquet(filename, index=False)
            else:
                QMessageBox.warning(
                    None,
                    "Export Data",
                    f"Unsupported file type: .{extension}"
                )
                return False
        except (OSError, ValueError, ImportError) as error:
            QMessageBox.warning(
                None,
                "Export Data",
                f"Could not export the dataset:\n{error}"
            )
            return False

        return True

    def has_data(self):
        return self.dataset_manager.has_data()

    def has_result(self):
        return self.dataset_manager.has_result()

    def _dataframe_json(self, dataframe):

        if dataframe is None:
            return None

        return {
            "columns": [str(column) for column in dataframe.columns],
            "data": dataframe.to_json(
                orient="records",
                date_format="iso"
            )
        }

    def _dataframe_from_json(self, data):

        if data is None:
            return None

        columns = data.get(
            "columns",
            []
        )

        json_data = data.get(
            "data",
            "[]"
        )

        # Empty dataframe
        if not json_data or json_data == "[]":

            return pd.DataFrame(
                columns=columns
            )

        df = pd.read_json(
            StringIO(json_data),
            orient="records"
        )

        # Restore the original column names
        if len(df.columns) == len(columns):
            df.columns = columns

        else:
            raise ValueError(
                "Saved dataframe column count does not "
                "match the loaded dataframe."
            )

        return df

    def get_project_data(self):

        dataframe = self.dataset_manager.get_dataframe()

        if dataframe is None:
            return None

        result = self.dataset_manager.get_result_dataframe()

        return {
            "version": 3,
            "source_file": self.dataset_manager.filename,

            "main": {
                "original": self._dataframe_json(
                    self.dataset_manager.original_dataframe
                ),
                "current": self._dataframe_json(
                    dataframe
                ),
                "operations": self.dataset_manager.get_operation_log()
            },

            "result": {
                "visible": result is not None,
                "current": (
                    None
                    if result is None
                    else self._dataframe_json(result)
                ),
                "operations": self.dataset_manager.get_result_operation_log()
            },

            "history": {
                "main": self.dataset_manager.get_history_snapshot(
                    "main",
                    self._dataframe_json
                ),
                "result": self.dataset_manager.get_history_snapshot(
                    "result",
                    self._dataframe_json
                )
            }
        }

    def load_project_data(self, project):
        """Load a single workspace from saved project data."""

        try:

            main = project.get("main", {})
            result = project.get("result", {})

            self.dataset_manager.load_project(
                filename=project.get("source_file"),

                original=self._dataframe_from_json(
                    main.get("original")
                ),

                current=self._dataframe_from_json(
                    main.get("current")
                ),

                operations=main.get(
                    "operations",
                    []
                ),

                result_dataframe=self._dataframe_from_json(
                    result.get("current")
                ),

                result_operations=result.get(
                    "operations",
                    []
                ),

                main_history=project.get(
                    "history",
                    {}
                ).get("main"),

                result_history=project.get(
                    "history",
                    {}
                ).get("result"),

                dataframe_from_json=self._dataframe_from_json
            )

            self.refresh()

            return True

        except (
            KeyError,
            TypeError,
            ValueError
        ) as error:

            QMessageBox.warning(
                self,
                "Open Project",
                f"Could not load workspace:\n{error}"
            )

            return False

        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:

            QMessageBox.warning(
                None,
                "Open Project",
                f"Could not load the project:\n{error}"
            )

            return False