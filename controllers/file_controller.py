import json
from io import StringIO

import pandas as pd

from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QMessageBox

from ui.dialogs.import_dialog import ImportDialog


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

            dataframe = self._project_dataframe(project["data"])
            original_dataframe = self._project_dataframe(
                project.get("original_data", project["data"])
            )
            operations = project.get("operations", [])

            if not isinstance(operations, list):
                raise ValueError("Project operations must be a list")

            self.dataset_manager.load_dataframe(
                project.get("source_file", filename),
                dataframe,
                original_dataframe,
                operations
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
    # FUTURE FILE OPERATIONS
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

        project = {
            "source_file": self.dataset_manager.filename,
            "operations": self.dataset_manager.get_operation_log(),
            "original_data": json.loads(
                self.dataset_manager.original_dataframe.to_json(
                    orient="table",
                    date_format="iso"
                )
            ),
            "data": json.loads(
                dataframe.to_json(
                    orient="table",
                    date_format="iso"
                )
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
        """Export the current main dataframe to a standard file format."""

        dataframe = self.dataset_manager.get_dataframe()

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