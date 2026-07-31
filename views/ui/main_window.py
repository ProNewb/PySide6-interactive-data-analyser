from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
)
from controllers.file_controller import FileController
from core.dataset_manager import DatasetManager

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        from controllers.file_controller import FileController
        self.dataset_manager = DatasetManager()

        self.file_controller = FileController(self.dataset_manager)
        self.initialise_window()
        self.build_ui()
        self.create_menu()
        self.create_status_bar()


    def initialise_window(self):
        self.setWindowTitle("Data Explorer")
        self.resize(1200, 800)

    def build_ui(self):
        """Construct all interface widgets."""

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        title = QLabel("Data Explorer")
        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)

        central_widget.setLayout(layout)


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