from PySide6.QtCore import Qt
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
from ui.dialogs.aggregation_dialog import AggregationDialog
from ui.dialogs.cleaning_dialog import CleaningDialog
from ui.dialogs.data_dialog import DataDialog
from ui.dataset_view import DatasetView
from ui.dialogs.settings_dialog import SettingsDialog
from ui.graph.graph_widget import GraphWidget
from ui.stats.statistics_widget import StatisticsWidget
from ui.menus.control_panel import ControlPanel
from ui.menus.main_menu import MainMenu
from ui.menus.status_bar import StatusBar
from ui.menus.selection_toolbar import SelectionToolbar
from ui.graph.graph_tab import GraphTab
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
        self.main_menu.settings_action.triggered.connect(
            self.open_options
        )
        self.main_menu.exit_action.triggered.connect(
            self.close
        )

        self.main_menu.filter_action.triggered.connect(
            self.open_filter_dialog
        )

        self.main_menu.undo_action.triggered.connect(
            self.undo_operation
        )

        self.main_menu.reset_action.triggered.connect(
            self.reset_operation
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
            "Current Selection",
            "selection"
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




    def open_filter_dialog(self):

        dataframe = self.get_target_dataframe()

        if dataframe is None:
            return

        dialog = DataDialog(
            dataframe,
            self
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

        target = self.target_combo.currentData()

        if target == "result":

            self.dataset_manager.set_result_dataframe(
                filtered_dataframe
            )

        else:

            self.dataset_manager.set_dataframe(
                filtered_dataframe,
                "Applied filter"
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

    def undo_operation(self):

        target = self.target_combo.currentData()

        # A selection is a temporary view of data,
        # so there is no history to undo on it.
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
        #enables the undo/reset actions when appropriate
        target = self.target_combo.currentData()

        self.main_menu.undo_action.setEnabled(
            target != "selection"
            and self.dataset_manager.can_undo(target)
        )

        self.main_menu.reset_action.setEnabled(
            target == "main"
            and self.dataset_manager.can_reset()
        )


    def open_aggregation_dialog(self):

        dataframe = self.get_target_dataframe()

        if dataframe is None:
            return

        dialog = AggregationDialog(
            dataframe,
            self
        )

        if not dialog.exec():
            return

        aggregation = dialog.get_aggregation()

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

        target = self.target_combo.currentData()

        if target == "result":

            self.dataset_manager.set_result_dataframe(
                aggregated_dataframe
            )

            self.main_menu.result_dataset_action.setChecked(
                True
            )

            

        else:

            self.dataset_manager.set_result_dataframe(
                aggregated_dataframe
            )

            self.main_menu.result_dataset_action.setChecked(
                True
            )
        
        self.refresh_views()




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

        if target == "selection":

            # Determine which view is currently active
            if self.result_view.isVisible():
                dataframe = (
                    self.result_view
                    .get_analysis_dataframe()
                )

            else:
                dataframe = (
                    self.main_view
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

        return None

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

            self.dataset_manager.set_dataframe(
                cleaned,
                "Clean data"
            )

            self.refresh_views()

    def open_options(self):

        dialog = SettingsDialog(
            self.settings_manager,
            self.theme_manager,
            self
        )

        dialog.exec()