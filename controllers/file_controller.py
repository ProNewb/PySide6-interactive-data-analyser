import json
from io import StringIO

import pandas as pd

from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QInputDialog

from ui.dialogs.import_dialog import ImportDialog

from dataclasses import dataclass

@dataclass
class ColumnInfo:

    name: str
    detected_type: str
    nullable: bool

class FileController:
    """Handle file-related operations for the application."""

    def __init__(self, dataset_manager):

        self.dataset_manager = dataset_manager

    # ==================================================
    # OPEN
    # ==================================================

    def open_file(self):
        """Open a supported dataset file."""

        filename, _ = QFileDialog.getOpenFileName(
            None,
            "Open Dataset",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;"
            "JSON Files (*.json);;Parquet Files (*.parquet);;"
            "All Files (*)"
        )

        # The user cancelled the file dialog.
        if not filename:
            return

        if filename.lower().endswith(".csv"):
            dialog = ImportDialog(filename)

            if not dialog.exec():
                return False

            self.dataset_manager.load_csv(
                filename,
                dialog.get_options()
            )
            return True

        try:
            dataframe = self._read_dataset(filename)
            self.dataset_manager.load_dataframe(filename, dataframe)
        except (OSError, ValueError, ImportError) as error:
            QMessageBox.warning(
                None,
                "Open Dataset",
                f"Could not open the dataset:\n{error}"
            )
            return False

        return True

    def import_dataset_for_join(self, parent=None):
        """Import a second dataset using the normal import workflow."""

        filename, _ = QFileDialog.getOpenFileName(
            parent,
            "Import Dataset for Join",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;"
            "JSON Files (*.json);;Parquet Files (*.parquet);;"
            "All Files (*)"
        )

        if not filename:
            return None

        try:
            if filename.lower().endswith(".csv"):
                dialog = ImportDialog(filename, parent)
                if not dialog.exec():
                    return None
                options = dialog.get_options()
                dataframe = self.dataset_manager.reader.read(
                    filename,
                    options
                )
                if options.manual_headers:
                    dataframe.columns = options.manual_headers
                return dataframe

            return self._read_dataset(filename)
        except (OSError, ValueError, ImportError) as error:
            QMessageBox.warning(
                parent,
                "Import Dataset",
                f"Could not import the dataset:\n{error}"
            )
            return None

    def open_project(self):
        """Open a saved project and restore its operations."""

        filename, _ = QFileDialog.getOpenFileName(
            None,
            "Open Project",
            "",
            "Project Files (*.json);;All Files (*)"
        )

        if not filename:
            return False

        try:
            with open(filename, "r", encoding="utf-8") as project_file:
                project = json.load(project_file)

            main = project["main"]
            result = project["result"]

            self.dataset_manager.load_project(
                filename=project.get("source_file", filename),
                original=self._project_dataframe(main["original"]),
                current=self._project_dataframe(main["current"]),
                operations=main["operations"],
                result_dataframe=(
                    None if not result["visible"]
                    else self._project_dataframe(result["current"])
                ),
                result_operations=result.get("operations", []),
                main_history=project.get("history", {}).get("main", {}),
                result_history=project.get("history", {}).get("result", {}),
                dataframe_from_json=self._project_dataframe
            )
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            QMessageBox.warning(
                None,
                "Open Project",
                f"Could not open the project:\n{error}"
            )
            return False

        return True

    @staticmethod
    def _project_dataframe(data):
        return pd.read_json(
            StringIO(json.dumps(data)),
            orient="table"
        )

    @staticmethod
    def _dataframe_json(dataframe):
        return json.loads(
            dataframe.to_json(
                orient="table",
                date_format="iso"
            )
        )

    @staticmethod
    def _read_dataset(filename):
        extension = filename.lower().rsplit(".", 1)[-1]

        if extension == "xlsx" or extension == "xls":
            return pd.read_excel(filename)

        if extension == "json":
            return pd.read_json(filename)

        if extension == "parquet":
            return pd.read_parquet(filename)

        raise ValueError(f"Unsupported file type: .{extension}")

    # ==================================================
    # PROJECT AND EXPORT OPERATIONS
    # ==================================================

    def save_project(self):
        """Save the current dataframe and applied operations as JSON."""

        dataframe = self.dataset_manager.get_dataframe()

        if dataframe is None:
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

        result = self.dataset_manager.get_result_dataframe()

        project = {

            "version": 3,
            "source_file": self.dataset_manager.filename,

            "main": {

                "original": self._dataframe_json(
                    self.dataset_manager.original_dataframe
                ),
                "current": self._dataframe_json(dataframe),
                "operations": self.dataset_manager.get_operation_log()
            },

            "result": {

                "visible": result is not None,

                "current": None if result is None else self._dataframe_json(result),
                "operations": self.dataset_manager.get_result_operation_log()
            }
        }

        project["history"] = {
            # Keep the complete descriptions above and the bounded state
            # snapshots here so saved projects preserve both auditability and
            # the existing five-entry undo/redo behavior.
            "main": self.dataset_manager.get_history_snapshot(
                "main",
                self._dataframe_json
            ),
            "result": self.dataset_manager.get_history_snapshot(
                "result",
                self._dataframe_json
            )
        }

        try:
            with open(filename, "w", encoding="utf-8") as project_file:
                json.dump(project, project_file, indent=2, default=str)
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

    def close_project(self):
        """Close the current file and clear its project state."""

        return self.dataset_manager.close_file()

    def detect_column_types(df):

        columns = []

        for name in df.columns:

            dtype = df[name].dtype

            if pd.api.types.is_integer_dtype(dtype):
                detected = "Integer"

            elif pd.api.types.is_float_dtype(dtype):
                detected = "Float"

            elif pd.api.types.is_bool_dtype(dtype):
                detected = "Boolean"

            elif pd.api.types.is_datetime64_any_dtype(dtype):
                detected = "Date"

            else:
                detected = "Text"

            columns.append(
                ColumnInfo(
                    name,
                    detected,
                    df[name].isna().any()
                )
            )

        return columns