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
        menu_bar = window.menuBar().addMenu("Data")
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
        self.data_menu = menu_bar.addMenu("Data")

        self.filter_action = QAction(
            "Filter",
            window
        )

        self.data_menu.addAction(
            self.filter_action
        )