from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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

from PySide6.QtGui import QIcon

from PySide6.QtGui import QFont

from controllers.file_controller import FileController
from controllers.analysis_controller import AnalysisController

from core.data_processor import DataProcessor
from core.dataset_manager import DatasetManager
from core.dataset_table import DataTable

from views.ui.data_dialog import DataDialog
from views.ui.graph_widget import GraphWidget
from views.ui.statistics_widget import StatisticsWidget
from views.ui.control_panel import ControlPanel
from views.ui.main_menu import MainMenu
from views.ui.status_bar import StatusBar
from views.ui.selection_toolbar import SelectionToolbar
from views.ui.graph_tab import GraphTab
class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.dataset_manager = DatasetManager()

        self.file_controller = FileController(
            self.dataset_manager
        )

        self.main_menu = MainMenu(self)
        self.graph_tab = GraphTab()
        self.controls = ControlPanel()
        self.table = DataTable()
        #self.dataset_manager = DatasetManager()
        self.data_processor = DataProcessor()
        #self.stats_widget = StatisticsWidget()#old
        self.selection_toolbar = SelectionToolbar(
        self.table
    )
        self.tabs = QTabWidget()
        
        self.initialise_window()
        self.build_ui()
        self.analysis_controller = AnalysisController(self.dataset_manager, self.table)
        
        ## main menu
        self.controls.load_button.clicked.connect(
            self.load_dataset
        )

        ## show csv
        self.controls.display_data_button.clicked.connect(
                self.display_dataframe
            ) 
        self.controls.stats_button.clicked.connect(
            self.show_statistics
        )
                ## main menu load

        self.main_menu.open_action.triggered.connect(
            self.load_dataset
        )
        ## exit
        self.main_menu.exit_action.triggered.connect(
            self.close
        )

        self.status = StatusBar()

        self.setStatusBar(
            self.status
        )

        self.table.selection_changed.connect(self.update_selection)
        self.main_menu.filter_action.triggered.connect(
            self.open_filter_dialog
        )

    def initialise_window(self):
        self.setWindowTitle("Data Explorer")
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
            


    def display_dataframe(self):

        if not self.dataset_manager.has_data():
            QMessageBox.warning(
                self,
                "No Dataset",
                "Please load a CSV first."
            )
            return

        df = self.dataset_manager.get_dataframe()

        self.table.display_dataframe(df)

    def load_dataset(self):

        self.file_controller.open_file()

        if self.dataset_manager.has_data():

            dataframe = self.dataset_manager.get_dataframe()

            self.table.display_dataframe(dataframe)
            self.graph_tab.set_dataframe(dataframe)
            #self.stats_widget.load_dataframe(dataframe)

            self.status.showMessage(
                "Dataset loaded successfully"
            )

    def show_statistics(self):

        self.analysis_controller.show_statistics(self)


    def build_tabs(self):

        self.tabs = QTabWidget()

        # =========================
        # TABLE TAB
        # =========================

        self.table_page = QWidget()

        table_layout = QHBoxLayout()

        table_layout.addWidget(self.table)
        table_layout.addWidget(self.selection_toolbar)

        self.table_page.setLayout(table_layout)


        # =========================
        # STATISTICS TAB
        # =========================

        self.statistics_page = QWidget()

        statistics_layout = QVBoxLayout()

        self.stats_widget = StatisticsWidget()

        self.statistics_button = QPushButton(
            "Update Statistics"
        )

        self.statistics_button.clicked.connect(
            self.pop_stats
        )

        statistics_layout.addWidget(
            self.stats_widget
        )

        statistics_layout.addWidget(
            self.statistics_button
        )

        self.statistics_page.setLayout(
            statistics_layout
        )


        # =========================
        # GRAPH TAB
        # =========================

        self.graph_page = self.graph_tab
        # =========================
        # ADD TABS
        # =========================

        self.tabs.addTab(
            self.table_page,
            "Table"
        )

        self.tabs.addTab(
            self.statistics_page,
            "Statistics"
        )

        self.tabs.addTab(
            self.graph_page,
            "Graphs"
        )

    def update_selection(self):

        selected = self.table.get_analysis_dataframe()

        print("Selection changed")

        if selected is None:
            print("No selection")
            return

        print(selected)

        self.graph_tab.set_dataframe(selected)

    def pop_stats(self):
        dataframe = self.table.get_analysis_dataframe()
        self.stats_widget.load_dataframe(dataframe)

    def update_graph_data(self):

        dataframe = self.table.get_analysis_dataframe()

        if dataframe is None:
            return

        self.graph_tab.set_dataframe(dataframe)

    def open_filter_dialog(self):

        dataframe = self.dataset_manager.get_dataframe()

        if dataframe is None:

            QMessageBox.warning(
                self,
                "No Data",
                "Please load a dataset first."
            )

            return

        dialog = DataDialog(
            dataframe,
            self
        )

        if dialog.exec():

            filter_data = dialog.get_filter()

            filtered_dataframe = self.data_processor.filter(
                dataframe,
                filter_data["column"],
                filter_data["operator"],
                filter_data["value"]
            )

            self.dataset_manager.set_dataframe(
                filtered_dataframe
            )

            self.refresh_views()


    def refresh_views(self):

            dataframe = self.dataset_manager.get_dataframe()

            if dataframe is None:
                return

            self.table.display_dataframe(dataframe)

            self.graph_tab.set_dataframe(dataframe)

            self.stats_widget.load_dataframe(dataframe)