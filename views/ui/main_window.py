from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
    QWidget,
    QLabel,
    QVBoxLayout,
    QTableWidget
)
from analysis.data_summary import DataSummary
from controllers.file_controller import FileController
from core.dataset_manager import DatasetManager
from views.ui.statistics_widget import StatisticsWidget

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.dataset_manager = DatasetManager()

        self.file_controller = FileController(self.dataset_manager)
        self.stats_widget = StatisticsWidget()
        self.initialise_window()
        self.build_ui()
        self.create_menu()
        self.create_status_bar()
        #self.create_button_layout()
        #self.display_dataframe()
        



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

        button_panel = self.create_button_panel()
        table = self.create_table()

        content_layout.addLayout(button_panel)
        content_layout.addWidget(table)

        self.main_layout.addLayout(content_layout)


    def create_button_panel(self):

        layout = QVBoxLayout()

        load_button = QPushButton("Load CSV")
        display_data_button = QPushButton("Display Data")
        stats_button = QPushButton("Statistics")
        graph_button = QPushButton("Graphs")

        layout.addWidget(load_button)
        layout.addWidget(display_data_button)
        layout.addWidget(stats_button)
        layout.addWidget(graph_button)
        layout.addStretch()

        load_button.clicked.connect(self.file_controller.open_file)
        load_button.clicked.connect(self.display_dataframe)
        display_data_button.clicked.connect(self.display_dataframe) 
        stats_button.clicked.connect(self.show_statistics)

        return layout

    def create_table(self):

        self.table = QTableWidget()

        return self.table


    def display_dataframe(self):
        if not self.dataset_manager.has_data():
            print("No data loaded")
            return

        df = self.dataset_manager.get_dataframe()

        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(
            [str(col) for col in df.columns]
        )

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))


    def create_menu(self):
        file_menu = self.menuBar().addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        open_action = QAction("Open", self)
        open_action.triggered.connect(
            self.file_controller.open_file
)
        file_menu.addAction("Save")
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)


    def create_status_bar(self):
                self.statusBar().showMessage("Ready")

    def create_stats_layout(self):
        self.stats_layout = QVBoxLayout()
        self.stats_label = QLabel("Statistics will be displayed here.")
        self.stats_layout.addWidget(self.stats_label)
        self.main_layout.addLayout(self.stats_layout)
        summary = DataSummary().generate(self.dataset_manager.get_dataframe())
        summary_button = QPushButton("Show Summary")
        summary_button.clicked.connect(self.show_summary)


    def show_statistics(self):

        if not self.dataset_manager.has_data():

            QMessageBox.warning(
                self,
                "No Dataset",
                "Please load a CSV first."
            )

            return

        self.stats_widget.load_dataframe(
            self.dataset_manager.get_dataframe()
        )

        self.stats_widget.show()




