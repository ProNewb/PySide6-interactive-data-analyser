from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
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
from ui.stats.statistics_widget import StatisticsWidget
from ui.menus.control_panel import ControlPanel
from ui.menus.main_menu import MainMenu
from ui.menus.status_bar import StatusBar
from ui.menus.selection_toolbar import SelectionToolbar
from ui.graph.graph_tab import GraphTab
from ui.model_tab import ModelTab
class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(    self,settings_manager,theme_manager):

        super().__init__()

        self.dataset_manager = DatasetManager()
        self.settings_manager = settings_manager
        self.theme_manager = theme_manager

        self.theme_manager.apply_theme(
            self.settings_manager.settings
        )
        self.file_controller = FileController(
            self.dataset_manager
        )

        self.data_processor = DataProcessor()

        self.main_menu = MainMenu(self)
        self.controls = ControlPanel()


      
        # ----------------------------------
        # Dataset views
        # ----------------------------------

        self.main_view = DatasetView(
            "Main Dataset"
        )

        self.result_view = DatasetView(
            "Result Dataset"
        )

        # Result starts hidden
        self.result_view.hide()

        # ----------------------------------
        # Main tabs
        # ----------------------------------

        self.tabs = QTabWidget()
      

        # ----------------------------------
        # Window
        # ----------------------------------

        self.initialise_window()
        self.build_ui()


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
            self.file_controller.save_project
        )
        self.main_menu.export_data_action.triggered.connect(
            self.file_controller.export_csv
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

        self.build_tabs()

        self.main_layout.addWidget(
            self.tabs
        )
   
    # retrieve data
    def load_dataset(self):

        self.file_controller.open_file()

        if self.dataset_manager.has_data():

            self.refresh_views()

            self.status.showMessage(
                "Dataset loaded successfully"
            )

    def load_project(self):

        if self.file_controller.open_project():

            self.main_menu.main_dataset_action.setChecked(
                self.dataset_manager.has_data()
            )
            self.main_menu.result_dataset_action.setChecked(
                self.dataset_manager.has_result()
            )

            self.refresh_views()

            self.status.showMessage(
                "Project loaded successfully"
            )

    def close_file(self):

        if not self.dataset_manager.has_data():
            return

        answer = QMessageBox.question(
            self,
            "Close File",
            "Close the current file and discard its loaded state?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        self.file_controller.close_project()
        self.refresh_views()
        self.main_menu.main_dataset_action.setChecked(False)
        self.main_menu.result_dataset_action.setChecked(False)
        self.status.showMessage("File closed")




    def build_tabs(self):
        '''Build each container'''
        self.tabs = QTabWidget()

        # ==================================
        # DATA TAB
        # ==================================

        data_page = QWidget()

        data_layout = QVBoxLayout(
            data_page
        )

        # ----------------------------------
        # Operation target
        # ----------------------------------

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

        self.target_combo.addItem(
            "Main Selection",
            "main_selection"
        )

        self.target_combo.addItem(
            "Result Selection",
            "result_selection"
        )

        target_layout.addWidget(
            self.target_combo
        )

        target_layout.addStretch()

        data_layout.addLayout(
            target_layout
        )

        # ----------------------------------
        # Dataset views
        # ----------------------------------

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

        data_layout.addWidget(
            self.splitter
        )

        # ----------------------------------
        # Add tab
        # ----------------------------------

        self.tabs.addTab(
            data_page,
            "Data"
        )



    def get_model_dataframes(self):
        """Provide current datasets to the Model tab without sharing widgets."""
        return [
            ("main", "Main Dataset", self.dataset_manager.get_dataframe()),
            ("result", "Result Dataset", self.dataset_manager.get_result_dataframe())
        ]




    def open_filter_dialog(self):

        target = self.target_combo.currentData()
        dataframes = {
            "main": self.dataset_manager.get_dataframe()
        }
        if self.dataset_manager.get_result_dataframe() is not None:
            dataframes["result"] = self.dataset_manager.get_result_dataframe()

        dataframe = dataframes.get(target)

        if dataframe is None:
            return

        dialog = DataDialog(
            dataframe,
            self,
            dataframes,
            target if target in dataframes else "main"
        )

        if not dialog.exec():
            return

        conditions = dialog.get_conditions()

        try:

            filtered_dataframe = (
                self.data_processor.filter(
                    dataframe,
                    conditions
                )
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Invalid Filter",
                str(error)
            )

            return

        target = dialog.get_target()

        target_name = "Result" if target == "result" else "Main"
        description = (
            f"{target_name}: filter where {conditions.describe()}"
        )

        if target == "result":

            self.dataset_manager.set_result_dataframe(
                filtered_dataframe,
                description
            )

        else:

            self.dataset_manager.set_dataframe(
                filtered_dataframe,
                description
            )

        self.refresh_views()


    def refresh_views(self):
        # refresh the view after a data operation
        dataframe = (
            self.dataset_manager
            .get_dataframe()
        )

        result = (
            self.dataset_manager
            .get_result_dataframe()
        )

        # Main dataset
        if dataframe is not None:

            self.main_view.set_dataframe(
                dataframe
            )

        else:

            self.main_view.clear()

        # Result dataset
        if result is not None:

            self.result_view.set_dataframe(
                result
            )

        else:

            self.result_view.clear()

        self.update_comparison_layout()
        self.update_data_actions()
        self.update_history_menus()
        #self.model_tab.refresh_data()
        
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

        target = self.target_combo.currentData()
        dataframes = {
            "main": self.dataset_manager.get_dataframe()
        }
        if self.dataset_manager.get_result_dataframe() is not None:
            dataframes["result"] = self.dataset_manager.get_result_dataframe()
        dataframe = dataframes.get(target)

        if dataframe is None:
            return

        dialog = AggregationDialog(
            dataframe,
            self,
            dataframes,
            target if target in dataframes else "main"
        )

        if not dialog.exec():
            return

        aggregation = dialog.get_aggregation()
        dataframe = dataframes[dialog.get_target()]

        try:

            aggregated_dataframe = (
                self.data_processor.aggregate(
                    dataframe,
                    aggregation
                )
            )

        except (ValueError, KeyError) as error:

            QMessageBox.warning(
                self,
                "Invalid Aggregation",
                str(error)
            )

            return

        # ----------------------------------
        # Check whether result exists
        # ----------------------------------

        existing_result = (
            self.dataset_manager
            .get_result_dataframe()
        )

        if existing_result is not None:

            answer = QMessageBox.question(
                self,
                "Overwrite Result?",
                "A result dataset already exists.\n\n"
                "Do you want to replace it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if answer != QMessageBox.Yes:
                return

        # ----------------------------------
        # Store result
        # ----------------------------------

        self.dataset_manager.set_result_dataframe(
            aggregated_dataframe,
            "Result: aggregate " + aggregation.describe()
        )

        self.main_menu.result_dataset_action.setChecked(
            True
        )

        self.refresh_views()

        self.status.showMessage(
            "Aggregation completed"
        )




    def get_target_dataframe(self):

        target = self.target_combo.currentData()

        if target == "main":

            return (
                self.dataset_manager
                .get_dataframe()
            )

        if target == "result":

            dataframe = (
                self.dataset_manager
                .get_result_dataframe()
            )

            if dataframe is None:

                QMessageBox.warning(
                    self,
                    "No Result",
                    "There is no result dataset available."
                )

                return None

            return dataframe

        if target == "main_selection":

            return self.main_view.get_analysis_dataframe()

        if target == "result_selection":

            dataframe = (
                self.result_view
                .get_analysis_dataframe()
            )

            if dataframe is None:

                QMessageBox.warning(
                    self,
                    "No Selection",
                    "No data is currently selected."
                )

                return None

            return dataframe

    def hide_main_view(self):

        self.main_menu.main_dataset_action.setChecked(
            False
        )

        self.update_comparison_layout()

    def hide_result_view(self):

        self.main_menu.result_dataset_action.setChecked(
            False
        )

        self.update_comparison_layout()

    def toggle_main_dataset(self, checked):

        self.update_comparison_layout()


    def toggle_result_dataset(self, checked):

        self.update_comparison_layout()

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

        dataframe = self.get_target_dataframe()

        if dataframe is None:
            return

        dialog = CleaningDialog(
            dataframe,
            self
        )

        if dialog.exec():

            cleaned = dialog.get_result()

            target = self.target_combo.currentData()
            target_name = "Result" if target == "result" else "Main"
            operation = dialog.get_operation()
            description = f"{target_name}: {operation.describe()}"

            if target == "main":

                self.dataset_manager.set_dataframe(
                    cleaned,
                    description
                )

            elif target == "result":

                self.dataset_manager.set_result_dataframe(
                    cleaned,
                    description
                )

            self.refresh_views()

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

        dataframe = self.dataset_manager.get_dataframe()

        if dataframe is None:
            QMessageBox.warning(
                self,
                "Join",
                "Load a main dataset before starting a join."
            )
            return

        imported_dataframe = self.file_controller.import_dataset_for_join(self)

        if imported_dataframe is None:
            return

        dialog = JoinDialog(
            dataframe,
            imported_dataframe,
            self,
            {
                "main": dataframe,
                **({"result": self.dataset_manager.get_result_dataframe()}
                   if self.dataset_manager.get_result_dataframe() is not None
                   else {})
            },
            "main"
        )

        if not dialog.exec():
            return

        config = dialog.get_config()
        target = dialog.get_target()
        target_dataframe = (
            self.dataset_manager.get_result_dataframe()
            if target == "result"
            else self.dataset_manager.get_dataframe()
        )

        try:
            joined = self.data_processor.join(
                target_dataframe,
                imported_dataframe,
                config
            )
        except (KeyError, TypeError, ValueError) as error:
            QMessageBox.warning(self, "Join", str(error))
            return

        if dialog.get_output() == "target":
            if target == "main":
                self.dataset_manager.set_dataframe(
                    joined,
                    "Main: add columns; " + config.describe()
                )
            else:
                self.dataset_manager.set_result_dataframe(
                    joined,
                    "Result: add columns; " + config.describe()
                )
        else:
            self.dataset_manager.set_result_dataframe(
                joined,
                "Result: " + config.describe()
            )

        self.main_menu.result_dataset_action.setChecked(True)
        self.refresh_views()


    def open_transform_dialog(self):

        target = self.target_combo.currentData()
        dataframes = {
            "main": self.dataset_manager.get_dataframe()
        }
        if self.dataset_manager.get_result_dataframe() is not None:
            dataframes["result"] = self.dataset_manager.get_result_dataframe()
        dataframe = dataframes.get(target)

        if dataframe is None:
            return

        dialog = TransformDialog(
            dataframe,
            self,
            dataframes,
            target if target in dataframes else "main"
        )

        if not dialog.exec():
            return

        config = dialog.get_transform()
        target = dialog.get_target()
        dataframe = dataframes[target]

        try:
            transformed = self.data_processor.transform(
                dataframe,
                config
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Transform",
                str(error)
            )
            return

        description = config.describe()

        if target == "result":
            self.dataset_manager.set_result_dataframe(
                transformed,
                description
            )
        else:
            self.dataset_manager.set_dataframe(
                transformed,
                description
            )

        self.refresh_views()
        self.status.showMessage("Transform completed")