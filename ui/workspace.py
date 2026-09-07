import json

from io import StringIO
from pathlib import Path

import pandas as pd

from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QInputDialog


from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QSplitter
)

from core.dataset_manager import DatasetManager
from ui.results_panel import ResultPanel
from ui.table.dataset_view import DatasetView
from controllers.file_controller import FileController
from PySide6.QtCore import Qt

class Workspace(QWidget):
    history_changed = Signal()
    """Represents a single analysis workspace.

        Each workspace owns:
            - one DatasetManager
            - one FileController
            - one main DatasetView
            - one ResultPanel containing zero or more result DatasetViews

        The MainWindow manages multiple Workspace instances as tabs.
        """
    main_visibility_changed = Signal(bool)
    result_visibility_changed = Signal(bool)
    def __init__(self, parent=None):
            super().__init__(parent)
            self.main_visible = True
            self.result_visible = False
            self.dataset_manager = DatasetManager()

            self.file_controller = FileController(
                self.dataset_manager
            )

            self.main_view = DatasetView(
                "Main Dataset",
                "main",
                workspace=self
            )

            self.result_panel = ResultPanel(
                workspace=self
            )

            self.result_panel.hide()

            self.splitter = QSplitter(Qt.Horizontal)

            self.splitter.addWidget(
                self.main_view
            )

            self.splitter.addWidget(
                self.result_panel
            )

            self.splitter.setSizes([
                1200,
                0
            ])

            layout = QVBoxLayout(self)
            layout.addWidget(self.splitter)

            self.main_view.close_requested.connect(
                self.hide_main_view
            )

            self.result_panel.result_added.connect(
                lambda view: view.close_requested.connect(
                    self.hide_result_panel
                )
            )
            self.result_panel.result_visibility_changed.connect(
                self.set_result_visible
            )
            self.refresh()
            self.result_panel.current_changed.connect(
                self.on_result_changed
            )
    # ======================================
    # REFRESH
    # ======================================

    def refresh(self):

        self.update_views()
        

    # ======================================
    # VIEWS
    # ======================================
    def update_views(self):

        # -------------------------
        # Main
        # -------------------------

        main = self.dataset_manager.get_dataframe()

        if (
            main is not None
            and not main.empty
        ):
            self.main_view.set_dataframe(main)
        else:
            self.main_view.clear()

        # -------------------------
        # Results
        # -------------------------

        results = self.dataset_manager.results

        # Add missing tabs
        while self.result_panel.tabs.count() < len(results):

            index = self.result_panel.tabs.count()
            result = results[index]

            self.result_panel.add_result(
                result.name,
                result.dataframe
            )

        # Update existing tabs
        for index, result in enumerate(results):

            view = self.result_panel.view_at(index)

            if view is None:
                continue

            view.set_dataframe(
                result.dataframe
            )

            self.result_panel.tabs.setTabText(
                index,
                result.name
            )

        # Remove tabs that no longer exist
        while self.result_panel.tabs.count() > len(results):

            index = self.result_panel.tabs.count() - 1

            view = self.result_panel.view_at(index)

            self.result_panel.tabs.removeTab(index)

            if view is not None:
                view.deleteLater()

        # -------------------------
        # Visibility
        # -------------------------

        self.update_comparison_layout()

    # ======================================
    # LAYOUT
    # ======================================

    def update_comparison_layout(self):

        main_available = (
            self.dataset_manager.has_data()
        )

        result_available = (
            self.dataset_manager.has_results()
        )

        self.main_view.setVisible(
            main_available and self.main_visible
        )

        self.result_panel.setVisible(
            result_available and self.result_visible
        )

        if (
            main_available
            and self.main_visible
            and result_available
            and self.result_visible
        ):

            self.splitter.setSizes([
                600,
                600
            ])

        elif main_available and self.main_visible:

            self.splitter.setSizes([
                1200,
                0
            ])

        elif result_available and self.result_visible:

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

    def export_dataset(
        self,
        dataframe,
        filename,
        include_index=False
    ):
        suffix = Path(filename).suffix.lower()

        if suffix == ".csv":
            dataframe.to_csv(filename, index=include_index)

        elif suffix == ".xlsx":
            dataframe.to_excel(filename, index=include_index)

        elif suffix == ".json":
            dataframe.to_json(
                filename,
                orient="records",
                date_format="iso"
            )

        elif suffix == ".parquet":
            dataframe.to_parquet(filename, index=include_index)

    def has_data(self):
        return self.dataset_manager.has_data()

    def has_result(self):
        return self.dataset_manager.has_results()

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

        return {
            "version": 5,
            "source_file": self.dataset_manager.filename,

            "main": {
                "original": self._dataframe_json(
                    self.dataset_manager.original_dataframe
                ),
                "current": self._dataframe_json(
                    self.dataset_manager.get_dataframe()
                ),
                "operations": self.dataset_manager.main.operations,
                "visible": self.main_visible,
            },

            "results": [
                {
                    "name": result.name,
                    "dataframe": self._dataframe_json(result.dataframe),
                    "operations": result.operations,
                }
                for result in self.dataset_manager.results
            ],

            "active_result": self.dataset_manager.active_result,
            "result_visible": self.result_visible,

            "history": {
                "main": self.dataset_manager.get_history_snapshot(
                target="main",
                dataframe_to_json=self._dataframe_json
                )
            }
        }

    def load_project_data(self, project):

        try:

            main = project.get("main", {})

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
                main_history=project.get(
                    "history",
                    {}
                ).get("main"),
                dataframe_from_json=self._dataframe_from_json
            )

            self.dataset_manager.results.clear()

            for saved in project.get("results", []):

                dataframe = self._dataframe_from_json(
                    saved.get("dataframe")
                )

                if dataframe is None:
                    continue

                index = self.dataset_manager.add_result(
                    dataframe,
                    saved.get("name", "Result")
                )

                self.dataset_manager.results[index].operations = (
                    saved.get("operations", [])
                )

            self.dataset_manager.active_result = project.get(
                "active_result",
                -1
            )

            self.main_visible = main.get(
                "visible",
                True
            )

            self.result_visible = project.get(
                "result_visible",
                False
            )

            self.refresh()

            return True

        except Exception as error:

            QMessageBox.warning(
                self,
                "Load Project",
                f"Could not load workspace:\n{error}"
            )

            return False
    
    def hide_main_view(self):
        self.set_main_visible(False)


    def show_main_view(self):
        self.set_main_visible(True)


    def hide_result_panel(self):
        self.result_visible = False
        self.update_comparison_layout()


    def show_result_panel(self):

        if self.result_panel.has_results():
            self.result_visible = True
            self.update_comparison_layout()


    def ensure_result_view(self):

        view = self.result_panel.current_view()

        if view is None:
            view = self.result_panel.add_result("Result")

        return view

    def set_main_visible(self, visible):

        self.main_visible = visible
        self.main_visibility_changed.emit(visible)
        self.update_comparison_layout()


    def set_result_visible(self, visible):

        self.result_visible = visible
        self.update_comparison_layout()
        self.result_visibility_changed.emit(visible)

    def create_result(
        self,
        dataframe,
        name="Result",
        description="Result created"
    ):
        index = self.dataset_manager.add_result(
            dataframe,
            name,
            description=description
        )

        result = self.dataset_manager.results[index]


        self.result_panel.add_result(
            result.name,
            result.dataframe
        )

        self.result_visible = True

        self.update_comparison_layout()

        return index

    def replace_current_result(
        self,
        dataframe,
        description="Result changed"
    ):
        result = self.dataset_manager.current_result()

        if result is None:
            return False

        index = self.dataset_manager.active_result
        if index < 0:
            return False

        self.dataset_manager.replace_result(
            dataframe,
            description,
            index=index
        )

        view = self.result_panel.view_at(index)

        if view is not None:
            view.set_dataframe(dataframe)

        self.update_comparison_layout()

        return True

    def on_result_changed(self, index):
        self.dataset_manager.set_active_result(index)

        # Refresh graphs/statistics for the newly selected tab
        view = self.result_panel.current_view()
        if view:
            view.update_analysis()

        # Tell MainWindow to update Undo/Redo toolbar
        self.history_changed.emit()

    def new_dataset(self):
        self.dataset_manager.new_dataset()
        self.update_views()