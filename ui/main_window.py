import json
from pathlib import Path

from PySide6.QtCore import QFileInfo, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QToolButton,
    QWidget,
    QLabel,
    QVBoxLayout
)
from PySide6.QtWidgets import QSplitter
from PySide6.QtGui import QAction, QIcon

from PySide6.QtGui import QFont

from controllers.file_controller import FileController
from controllers.analysis_controller import AnalysisController
from ui.workspace import Workspace
from core import settings_manager, theme_manager
from core.condition_group import ConditionGroup
from core.conditions import Condition
from core.data_processor import DataProcessor
from core.dataset_manager import DatasetManager
from core.dataset_table import DataTable
from core.settings_manager import SettingsManager
from core.theme_manager import ThemeManager
from ui.dialogs import data_dialog
from ui.dialogs.transform_dialog import TransformDialog
from ui.dialogs.aggregation_dialog import AggregationDialog
from ui.dialogs.cleaning_dialog import CleaningDialog
from ui.dialogs.data_dialog import DataDialog
from ui.dataset_view import DatasetView
from ui.dialogs.join_dialog import JoinDialog
from ui.dialogs.settings_dialog import SettingsDialog
from ui.graph.graph_widget import GraphWidget
from ui.helpers.target_combo import TargetCombo
from ui.stats.statistics_widget import StatisticsWidget
from ui.menus.control_panel import ControlPanel
from ui.menus.main_menu import MainMenu
from ui.menus.status_bar import StatusBar
from ui.menus.selection_toolbar import SelectionToolbar
from ui.graph.graph_tab import GraphTab
from ui.model_tab import ModelTab
class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, settings_manager, theme_manager):

        super().__init__()

        self.settings_manager = settings_manager
        self.theme_manager = theme_manager

        # Workspace container
        self.workspaces = QTabWidget()
        self.workspaces.setTabsClosable(True)
        self.workspaces.tabCloseRequested.connect(self.close_workspace)

        #self.create_workspace("Untitled")

        self.workspaces.setStyleSheet("""
            QTabBar::tab {
                min-width: 100px;
                max-width: 180px;
            }
        """)


        self.theme_manager.apply_theme(
            self.settings_manager.settings
        )

        self.t_combo = TargetCombo()
        self.data_processor = DataProcessor()

        self.main_menu = MainMenu(self)
        self.controls = ControlPanel()

        # UI
        self.initialise_window()
        self.build_ui()

        # Create initial workspace
        self.create_workspace()

        self.status = StatusBar()
        self.setStatusBar(self.status)

        # Workspace changes
        self.workspaces.currentChanged.connect(
            self.workspace_changed
        )


      

        # ----------------------------------
        # Window
        # ----------------------------------



        # ----------------------------------
        # Signals
        # ----------------------------------

        self.controls.load_button.clicked.connect(
            self.load_dataset
        )

        self.main_menu.open_action.triggered.connect(
            self.load_dataset
        )
        self.main_menu.open_project_action.triggered.connect(
            self.load_project
        )
        self.main_menu.save_project_action.triggered.connect(
            self.save_project
        )

        self.main_menu.export_data_action.triggered.connect(
            self.export_data
        )
        self.main_menu.close_file_action.triggered.connect(
            self.close_file
        )
        self.main_menu.settings_action.triggered.connect(
            self.open_options
        )
        self.main_menu.exit_action.triggered.connect(
            self.close
        )

        self.main_menu.filter_action.triggered.connect(
            self.open_filter_dialog
        )

        self.main_menu.undo_button.triggered.connect(
            self.undo_operation
        )
        self.main_menu.transform_action.triggered.connect(
            self.open_transform_dialog
        )
        self.main_menu.join_action.triggered.connect(
            self.open_join_dialog
        )
        self.main_menu.reset_action.triggered.connect(
            self.reset_operation
        )
        self.main_menu.redo_button.setEnabled(
            self.dataset_manager.can_redo()
        )
        self.main_menu.aggregate_action.triggered.connect(
            self.open_aggregation_dialog
        )
        self.main_view.close_requested.connect(
            self.hide_main_view
        )

        self.result_view.close_requested.connect(
            self.hide_result_view
        )
        self.main_menu.main_dataset_action.triggered.connect(
            self.toggle_main_dataset
        )

        self.main_menu.result_dataset_action.triggered.connect(
            self.toggle_result_dataset
        )
        self.main_menu.clean_action.triggered.connect(
            self.open_cleaning_dialog
        )

        #####context menu
        self.main_view.filter_requested.connect(
            self.open_filter_dialog
        )
        self.main_view.aggregate_requested.connect(
            self.open_aggregation_dialog
        )
        self.main_view.join_requested.connect(
            self.open_join_dialog
        )
        self.main_view.transform_requested.connect(
            self.open_transform_dialog
        )
        self.main_view.clean_requested.connect(
            self.open_cleaning_dialog
        )
        self.status = StatusBar()

        self.setStatusBar(
            self.status
        )

    # Display
    def initialise_window(self):
            if self.settings_manager.settings.start_maximized:
                self.showMaximized()
            else:
                self.resize(1200, 800)



    def build_ui(self):

        self.create_central_widget()
        self.create_title()
        self.create_content_area()
        


    def create_central_widget(self):

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

    def create_title(self):

        title = QLabel("Data Explorer")
        title.setAlignment(Qt.AlignCenter)

        self.main_layout.addWidget(title)


    def create_content_area(self):

        self.create_operation_controls()

        self.main_layout.addWidget(
            self.workspaces
        )
    def create_operation_controls(self):

        target_layout = QHBoxLayout()

        target_layout.addWidget(
            QLabel("Operate on:")
        )

        self.target_combo = QComboBox()

        self.target_combo.addItem(
            "Main Dataset",
            "main"
        )

        self.target_combo.addItem(
            "Result Dataset",
            "result"
        )

        self.use_selection = QCheckBox(
            "Use selection"
        )
        self.allow_cross_tab_selection = QCheckBox(
            "cross-tab selection"
        )
        target_layout.addWidget(
            self.target_combo
        )

        target_layout.addWidget(
            self.use_selection
        )
        target_layout.addWidget(
            self.allow_cross_tab_selection
        )
        target_layout.addStretch()

        self.main_layout.addLayout(
            target_layout
        )
    # retrieve data
    def load_dataset(self):

        current_workspace = self.workspace

        # Reuse the initial empty Untitled tab
        if (
            self.workspaces.count() == 1
            and current_workspace is not None
            and not current_workspace.dataset_manager.has_data()
        ):
            workspace = current_workspace
            created_new = False

        else:
            workspace = self.create_workspace("Untitled")
            created_new = True

        # Open the file
        if not workspace.file_controller.open_file():

            if created_new:

                index = self.workspaces.indexOf(workspace)

                if index >= 0:
                    self.workspaces.removeTab(index)

                workspace.deleteLater()

            return

        # Refresh only this workspace
        workspace.refresh()

        # Rename the tab
        filename = workspace.dataset_manager.filename

        if filename:
            title = Path(filename).stem
        else:
            title = "Untitled"

        index = self.workspaces.indexOf(workspace)

        if index >= 0:
            self.workspaces.setTabText(
                index,
                title
            )
            self.workspaces.setCurrentIndex(index)

        self.update_workspace_controls()

        self.status.showMessage(
            f"Loaded {title}"
        )

    def load_project(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "Project Files (*.json);;All Files (*)"
        )

        if not filename:
            return

        workspace = Workspace(self)

        if not workspace.load_project():
            workspace.deleteLater()
            return

        project_name = QFileInfo(filename).baseName()

        index = self.workspaces.addTab(
            workspace,
            project_name
        )

        self.workspaces.setCurrentIndex(index)

    def close_file(self):

        index = self.workspaces.currentIndex()

        if index >= 0:
            self.close_workspace(index)


    def open_filter_dialog(self):

        target, dataframe = self.get_dialog_dataframe()


        dialog = DataDialog(
            self.get_available_datasets(),
            self,
            current=f"{self.workspaces.tabText(self.workspaces.currentIndex())} • Main",
            use_selection=self.use_selection.isChecked()
        )
        if not dialog.exec():
            return

        workspace = dialog.get_workspace()
        target = dialog.get_target()
        dataframe = dialog.get_dataframe()

        config = dialog.get_conditions()

        try:
            result = self.data_processor.filter(
                dataframe,
                config
            )
        except ValueError as error:
            QMessageBox.warning(
                self,
                "Filter Failed",
                str(error)
            )
            return

        if target == "main":
            workspace.dataset_manager.set_dataframe(
                result,
                config.describe()
            )
        else:
            workspace.dataset_manager.set_result_dataframe(
                result,
                config.describe()
            )

        workspace.refresh()
        self.update_workspace_controls()


    def refresh_views(self):

        workspace = self.workspace

        if workspace is None:
            return

        workspace.refresh()

        self.update_workspace_controls()
        
    def undo_operation(self):

        target = self.target_combo.currentData()

        if target in (
            "main_selection",
            "result_selection"
        ):

            QMessageBox.information(
                self,
                "Undo",
                "Undo cannot be applied directly to a selection."
            )

            return

        description = self.dataset_manager.undo(target)

        if description is not None:

            self.refresh_views()

            self.update_data_actions()

            self.status.showMessage(
                f"Undid: {description}"
            )

    def reset_operation(self):

        if not self.dataset_manager.can_reset():
            return

        result = QMessageBox.question(
            self,
            "Reset Data",
            "Are you sure you want to reset the dataset?\n\n"
            "All modifications will be removed.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if result == QMessageBox.Yes:

            if self.dataset_manager.reset():

                self.refresh_views()
                self.update_data_actions()

                self.status.showMessage(
                    "Dataset reset to original state"
                )


    def update_data_actions(self):

        target = self.target_combo.currentData()

        is_dataset = target in (
            "main",
            "result"
        )

        self.main_menu.undo_button.setEnabled(
            is_dataset
            and self.dataset_manager.can_undo(target)
        )

        self.main_menu.redo_button.setEnabled(
            is_dataset
            and self.dataset_manager.can_redo(target)
        )

        self.main_menu.reset_action.setEnabled(
            target == "main"
            and self.dataset_manager.can_reset()
        )


    def open_aggregation_dialog(self):

        target, dataframe = self.get_dialog_dataframe()

        if dataframe is None:
            QMessageBox.warning(
                self,
                "Aggregate",
                "There is no dataset available to aggregate."
            )
            return

        dialog = AggregationDialog(
            self.get_available_datasets(),
            self,
            current=(
                f"{self.workspaces.tabText(self.workspaces.currentIndex())}"
                f" • Main"
            ),
            use_selection=self.use_selection.isChecked()
        )

        if not dialog.exec():
            return

        workspace = dialog.get_workspace()
        dataframe = dialog.get_dataframe()
        config = dialog.get_aggregation()

        try:
            result = self.data_processor.aggregate(
                dataframe,
                config
            )
        except ValueError as error:
            QMessageBox.warning(
                self,
                "Aggregation Failed",
                str(error)
            )
            return

        workspace.dataset_manager.set_result_dataframe(
            result,
            config.describe()
        )

        workspace.refresh()
        self.update_workspace_controls()

        self.status.showMessage(
            "Aggregation created result dataset"
        )


    def get_target_dataframe(self):
        target = self.target_combo.currentData()

        if target == "main":
            view = self.main_view
        else:
            view = self.result_view

        if self.use_selection.isChecked():
            return view.get_analysis_dataframe()

        return view.get_dataframe()

    def hide_main_view(self):

        self.main_menu.main_dataset_action.setChecked(False)

        if self.workspace:
            self.workspace.main_view.hide()

    def hide_result_view(self):

        self.main_menu.result_dataset_action.setChecked(
            False
        )

        if self.workspace:
            self.workspace.result_view.hide()

    def toggle_main_dataset(self, checked):

        workspace = self.workspace

        if workspace is None:
            return

        workspace.main_view.setVisible(
            checked
        )


    def toggle_result_dataset(self, checked):

        workspace = self.workspace

        if workspace is None:
            return

        workspace.result_view.setVisible(
            checked
        )

    def update_comparison_layout(self):
        '''creates a split layout when new views are created/removed'''
        main_available = (
            self.dataset_manager.get_dataframe()
            is not None
        )

        result_available = (
            self.dataset_manager.get_result_dataframe()
            is not None
        )

        main_checked = (
            self.main_menu.main_dataset_action.isChecked()
        )

        result_checked = (
            self.main_menu.result_dataset_action.isChecked()
        )

        main_visible = main_available and main_checked
        result_visible = result_available and result_checked

        self.main_view.setVisible(main_visible)
        self.result_view.setVisible(result_visible)

        if main_visible and result_visible:

            self.splitter.setSizes([
                600,
                600
            ])

        elif main_visible:

            self.splitter.setSizes([
                1200,
                0
            ])

        elif result_visible:

            self.splitter.setSizes([
                0,
                1200
            ])

    def open_cleaning_dialog(self):

        target, dataframe = self.get_dialog_dataframe()

        if dataframe is None:
            QMessageBox.warning(
                self,
                "Clean Data",
                "There is no dataset available to clean."
            )
            return

        dialog = CleaningDialog(
            self.get_available_datasets(),
            self,
            current=(
                f"{self.workspaces.tabText(self.workspaces.currentIndex())}"
                f" • Main"
            ),
            use_selection=self.use_selection.isChecked()
        )

        dialog.set_dataframe(dataframe)

        if not dialog.exec():
            return

        workspace = dialog.get_workspace()
        target = dialog.get_target()
        result = dialog.get_result()

        if result is None:
            QMessageBox.warning(
                self,
                "Cleaning Failed",
                "No cleaning result was produced."
            )
            return

        config = dialog.get_operation()

        if target == "main":

            workspace.dataset_manager.set_dataframe(
                result,
                config.describe()
            )

        else:

            workspace.dataset_manager.set_result_dataframe(
                result,
                config.describe()
            )

        workspace.refresh()
        self.update_workspace_controls()

        self.status.showMessage(
            "Cleaning completed"
        )

    def open_options(self):

        dialog = SettingsDialog(
            self.settings_manager,
            self.theme_manager,
            self
        )

        dialog.exec()

    def confirm_result_overwrite(self):

        if (
            self.dataset_manager
            .get_result_dataframe()
            is None
        ):
            return True

        answer = QMessageBox.question(
            self,
            "Overwrite Result?",
            "A result dataset already exists.\n\n"
            "Do you want to replace it?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        return answer == QMessageBox.Yes

    def update_undo_menu(self):

        menu = self.main_menu.undo_history_menu
        menu.clear()

        target = self.target_combo.currentData()

        if target not in ("main", "result"):
            return

        history = self.dataset_manager.get_undo_history(
            target
        )

        for operation in reversed(history):

            action = menu.addAction(
                operation.description
            )

            action.triggered.connect(
                lambda checked=False,
                op=operation:
                self.undo_to_operation(op)
            )

    def redo_operation(self):

        target = self.target_combo.currentData()

        if target in (
            "main_selection",
            "result_selection"
        ):

            QMessageBox.information(
                self,
                "Redo",
                "Redo cannot be applied directly to a selection."
            )

            return

        description = self.dataset_manager.redo(
            target
        )

        if description is not None:

            self.refresh_views()

            self.status.showMessage(
                f"Redid: {description}"
            )

    def update_redo_menu(self):

        menu = self.main_menu.redo_history_menu
        menu.clear()

        target = self.target_combo.currentData()

        if target not in ("main", "result"):
            return

        history = self.dataset_manager.get_redo_history(
            target
        )

        for operation in reversed(history):

            action = menu.addAction(
                operation.description
            )

            action.triggered.connect(
                lambda checked=False,
                op=operation:
                self.redo_to_operation(op)
            )

    def update_history_menus(self):

        target = self.target_combo.currentData()

        # Only datasets have history
        if target not in ("main", "result"):

            self.main_menu.undo_history_menu.clear()
            self.main_menu.redo_history_menu.clear()
            return

        # ---------------- Undo ----------------

        undo_menu = self.main_menu.undo_history_menu
        undo_menu.clear()

        history = self.dataset_manager.get_undo_history(target)

        for i, operation in enumerate(reversed(history), 1):

            text = f"{i}. {operation.description}"

            action = undo_menu.addAction(text)

            action.triggered.connect(
                lambda checked=False, steps=i: self.undo_multiple(steps)
            )

        # ---------------- Redo ----------------

        redo_menu = self.main_menu.redo_history_menu
        redo_menu.clear()

        history = self.dataset_manager.get_redo_history(target)

        for i, operation in enumerate(reversed(history), 1):

            text = f"{i}. {operation.description}"

            action = redo_menu.addAction(text)

            action.triggered.connect(
                lambda checked=False, steps=i: self.redo_multiple(steps)
            )
    def undo_multiple(self, steps):

        for _ in range(steps):
            self.undo_operation()


    def redo_multiple(self, steps):

        for _ in range(steps):
            self.redo_operation()

    def transform_operation(self):
        """Backward-compatible entry point for the Transform menu action."""
        self.open_transform_dialog()

    def join_operation(self):
        """Backward-compatible entry point for the Join menu action."""
        self.open_join_dialog()

    def open_join_dialog(self):

        if self.workspace is None:
            return

        dialog = JoinDialog(
            self.get_available_datasets(),
            self,
            current=(
                f"{self.workspaces.tabText(self.workspaces.currentIndex())}"
                f" • Main"
            ),
            use_selection=self.use_selection.isChecked()
        )

        if not dialog.exec():
            return

        workspace = dialog.get_workspace()

        left_dataframe = dialog.get_left_dataframe()
        right_dataframe = dialog.get_right_dataframe()

        config = dialog.get_config()

        if (
            left_dataframe is None
            or right_dataframe is None
        ):
            QMessageBox.warning(
                self,
                "Join Failed",
                "Both datasets must contain data."
            )
            return

        try:

            result = self.data_processor.join(
                left_dataframe,
                right_dataframe,
                config
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Join Failed",
                str(error)
            )

            return

        if result is None:
            QMessageBox.warning(
                self,
                "Join Failed",
                "The join did not produce a result."
            )
            return

        if config.mode == "target":

            workspace.dataset_manager.set_dataframe(
                result,
                config.describe()
            )

        else:

            workspace.dataset_manager.set_result_dataframe(
                result,
                config.describe()
            )

        workspace.refresh()
        self.update_workspace_controls()

        self.status.showMessage(
            "Join completed"
        )
        
    def open_transform_dialog(self):

        target, dataframe = self.get_dialog_dataframe()


        dialog = TransformDialog(
            self.get_available_datasets(),
            self,
            current=f"{self.workspaces.tabText(self.workspaces.currentIndex())} • Main",
            use_selection=self.use_selection.isChecked()
        )
        if not dialog.exec():
            return

        workspace = dialog.get_workspace()
        target = dialog.get_target()
        dataframe = dialog.get_dataframe()

        config = dialog.get_transform()

        result = self.data_processor.transform(dataframe, config)

        if target == "main":
            workspace.dataset_manager.set_dataframe(result, config.describe())
        else:
            workspace.dataset_manager.set_result_dataframe(result, config.describe())

        workspace.refresh()


    def get_target_dataframes(self):
        """Return all available datasets respecting Use Selection."""

        dataframes = {}

        main = self.get_dataframe_for_target("main")

        if main is not None:
            dataframes["main"] = main

        result = self.get_dataframe_for_target("result")

        if result is not None:
            dataframes["result"] = result

        return dataframes

    def get_dataframe_for_target(self, target, use_selection=None):
        """Return a dataset, optionally restricted to the current selection."""

        if target == "main":
            dataframe = self.dataset_manager.get_dataframe()
            view = self.main_view
        else:
            dataframe = self.dataset_manager.get_result_dataframe()
            view = self.result_view

        if dataframe is None:
            return None

        if use_selection is None:
            use_selection = self.use_selection.isChecked()

        if use_selection:
            return view.get_analysis_dataframe()

        return dataframe
    
    def get_dialog_dataframe(self):
        """Return the current target dataframe."""

        target = self.target_combo.currentData()

        dataframe = self.get_dataframe_for_target(target)

        return target, dataframe

    def create_workspace(self, title="Untitled"):

        workspace = Workspace(self)

        index = self.workspaces.addTab(
            workspace,
            title
        )

        self.workspaces.setCurrentIndex(index)

        return workspace
    
    def save_project(self):

        workspaces = []

        for index, workspace in enumerate(self.workspaces):

            data = workspace.get_project_data()

            if data is None:
                continue

            workspaces.append({
                "name": self.tab_widget.tabText(index),
                "data": data
            })

        if not workspaces:
            QMessageBox.information(
                self,
                "Save Project",
                "There are no datasets to save."
            )
            return False

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project",
            "",
            "Project Files (*.json);;All Files (*)"
        )

        if not filename:
            return False

        if not filename.lower().endswith(".json"):
            filename += ".json"

        project = {
            "version": 4,
            "current_workspace": self.tab_widget.currentIndex(),
            "workspaces": workspaces
        }

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
                self,
                "Save Project",
                f"Could not save the project:\n{error}"
            )

            return False

        return True


    def export_data(self):

        if self.workspace is None:
            return

        self.workspace.export_csv()

    @property
    def workspace(self):
        """Return the currently active workspace."""

        return self.workspaces.currentWidget()


    @property
    def dataset_manager(self):
        """Return the active workspace's DatasetManager."""

        workspace = self.workspace

        if workspace is None:
            return None

        return workspace.dataset_manager


    @property
    def main_view(self):
        """Return the active workspace's main view."""

        workspace = self.workspace

        if workspace is None:
            return None

        return workspace.main_view


    @property
    def result_view(self):
        """Return the active workspace's result view."""

        workspace = self.workspace

        if workspace is None:
            return None

        return workspace.result_view

    def workspace_changed(self, index):

        if index < 0:
            return

        workspace = self.workspaces.widget(index)

        if workspace is None:
            return

        self.update_workspace_controls()

    def close_workspace(self, index):

        workspace = self.workspaces.widget(index)

        if workspace is None:
            return

        # If there is data, ask before closing
        if workspace.dataset_manager.has_data():

            answer = QMessageBox.question(
                self,
                "Close Dataset",
                "Close this dataset?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if answer != QMessageBox.Yes:
                return

        self.workspaces.removeTab(index)

        workspace.deleteLater()

        # Keep at least one empty workspace
        if self.workspaces.count() == 0:
            self.create_workspace("Untitled")

    def update_workspace_controls(self):

        workspace = self.workspace

        if workspace is None:
            return

        manager = workspace.dataset_manager

        self.main_menu.main_dataset_action.setChecked(
            manager.has_data()
        )

        self.main_menu.result_dataset_action.setChecked(
            manager.has_result()
        )

        self.update_data_actions()
        self.update_history_menus()


    @property
    def file_controller(self):

        workspace = self.workspace

        if workspace is None:
            return None

        return workspace.file_controller

    def get_available_datasets(self):

        datasets = {}

        for i in range(self.workspaces.count()):

            ws = self.workspaces.widget(i)
            name = self.workspaces.tabText(i)

            if ws.has_data():
                datasets[f"{name} • Main"] = {
                    "workspace": ws,
                    "target": "main",
                    "dataframe": ws.dataset_manager.get_dataframe(),
                    "view": ws.main_view
                }

            if ws.has_result():
                datasets[f"{name} • Result"] = {
                    "workspace": ws,
                    "target": "result",
                    "dataframe": ws.dataset_manager.get_result_dataframe(),
                    "view": ws.result_view
                }

        return datasets