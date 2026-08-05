from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QWidget,
    QLabel,
    QVBoxLayout
)

from controllers.file_controller import FileController
from controllers.analysis_controller import AnalysisController

from core.dataset_manager import DatasetManager
from core.dataset_table import DataTable

from views.ui.statistics_widget import StatisticsWidget
from views.ui.control_panel import ControlPanel
from views.ui.main_menu import MainMenu
from views.ui.status_bar import StatusBar
from views.ui.selection_toolbar import SelectionToolbar

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.dataset_manager = DatasetManager()

        self.file_controller = FileController(
            self.dataset_manager
        )

        self.main_menu = MainMenu(self)

        self.controls = ControlPanel()
        self.table = DataTable()
        self.stats_widget = StatisticsWidget()
        self.selection_toolbar = SelectionToolbar(
        self.table
    )
        
        self.initialise_window()
        self.build_ui()
        self.analysis_controller = AnalysisController(self.dataset_manager)
        
        ## main menu
        self.controls.load_button.clicked.connect(
            self.load_dataset
        )

        ## show csv
        self.controls.display_data_button.clicked.connect(
                self.display_dataframe
            ) 
        self.controls.stats_button.clicked.connect(
            lambda:
            self.analysis_controller.show_statistics(self)
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

        content_layout = QHBoxLayout()
        button_panel = self.controls
        #button_panel = self.create_button_panel()
        #table = self.datatable.create_table()

        content_layout.addWidget(button_panel)
        #content_layout.addWidget(table)
        content_layout.addWidget(self.table)
        self.main_layout.addLayout(content_layout)



        content_layout.addWidget(
            self.selection_toolbar
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

            self.stats_widget.load_dataframe(dataframe)

            self.status.showMessage(
                "Dataset loaded successfully"
            )