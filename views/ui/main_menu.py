from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
class MainMenu:

    def __init__(self, window):

        self.file_menu = window.menuBar().addMenu("File")

        self.open_action = QAction(
            "Open",
            window
        )
        
        self.exit_action = QAction(
            "Exit",
            window
        )

        self.file_menu.addAction(
            self.open_action
        )

        self.file_menu.addAction(
            self.exit_action
        )