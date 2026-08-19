from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
class MainMenu:
    '''Main menu toolbar'''
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
## filter
        self.filter_action = QAction(
            "Filter",
            window
        )

        self.data_menu.addAction(
            self.filter_action
        )

## aggregation
        self.aggregate_action = QAction(
            "Aggregate",
            window
        )

        self.data_menu.addAction(
            self.aggregate_action
        )
## undo

        self.undo_action = QAction(
            "Undo",
            window
        )
## reset
        self.reset_action = QAction(
            "Reset",
            window
        )

        self.undo_action.setEnabled(False)
        self.reset_action.setEnabled(False)

        self.data_menu.addAction(
            self.undo_action
        )

        self.data_menu.addAction(
            self.reset_action
        )

    # view menu

        self.view_menu = menu_bar.addMenu("View")

        self.main_dataset_action = QAction(
            "Main Dataset",
            window
        )
        self.main_dataset_action.setCheckable(True)
        self.main_dataset_action.setChecked(True)

        self.result_dataset_action = QAction(
            "Result Dataset",
            window
        )
        self.result_dataset_action.setCheckable(True)
        self.result_dataset_action.setChecked(False)

        self.view_menu.addAction(
            self.main_dataset_action
        )

        self.view_menu.addAction(
            self.result_dataset_action
        )

        # Clean menu
        self.clean_menu = window.menuBar().addMenu("Clean")
        self.clean_action = QAction(
            "Clean",
            window
        )

        self.clean_menu.addAction(
            self.clean_action
        )