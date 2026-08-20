from PySide6.QtWidgets import (
    QMenu,
    QToolButton
)

from PySide6.QtGui import QAction
from PySide6.QtCore import Qt


class MainMenu:
    """Creates the application's menus and main toolbar."""

    def __init__(self, window):

        # ==================================================
        # TOOLBAR
        # ==================================================

        self.toolbar = window.addToolBar(
            "Main Toolbar"
        )

        # ==================================================
        # FILE MENU
        # ==================================================

        self.file_menu = (
            window.menuBar()
            .addMenu("File")
        )

        self.open_action = QAction(
            "Open File",
            window
        )

        self.open_project_action = QAction(
            "Open Project",
            window
        )

        self.save_project_action = QAction(
            "Save Project",
            window
        )

        self.export_data_action = QAction(
            "Export Data",
            window
        )

        self.close_file_action = QAction(
            "Close File",
            window
        )

        self.settings_action = QAction(
            "Settings",
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
            self.open_project_action
        )

        self.file_menu.addAction(
            self.save_project_action
        )

        self.file_menu.addAction(
            self.export_data_action
        )

        self.file_menu.addAction(
            self.close_file_action
        )

        self.file_menu.addAction(
            self.settings_action
        )

        self.file_menu.addAction(
            self.exit_action
        )

        # ==================================================
        # DATA MENU
        # ==================================================

        self.data_menu = (
            window.menuBar()
            .addMenu("Data")
        )

        # ----------------------------------
        # Filter
        # ----------------------------------

        self.filter_action = QAction(
            "Filter",
            window
        )

        self.data_menu.addAction(
            self.filter_action
        )

        # ----------------------------------
        # Aggregate
        # ----------------------------------

        self.aggregate_action = QAction(
            "Aggregate",
            window
        )

        self.data_menu.addAction(
            self.aggregate_action
        )
        # ==================================================
        # JOIN MENU
        # ==================================================


        self.join_action = QAction(
            "Join",
            window
        )

        self.data_menu.addAction(
            self.join_action
        )
        # ==================================================
        # Transform MENU
        # ==================================================


        self.transform_action = QAction(
            "Transform",
            window
        )

        self.data_menu.addAction(
            self.transform_action
        )
        # ----------------------------------
        # Reset
        # ----------------------------------

        self.reset_action = QAction(
            "Reset",
            window
        )

        self.reset_action.setEnabled(
            False
        )

        self.data_menu.addAction(
            self.reset_action
        )

        # ==================================================
        # UNDO
        # ==================================================

        self.undo_button = QToolButton(
            window
        )

        self.undo_button.setText(
            "Undo"
        )

        self.undo_button.setToolButtonStyle(
            Qt.ToolButtonTextOnly
        )

        self.undo_button.setPopupMode(
            QToolButton.MenuButtonPopup
        )

        self.undo_history_menu = QMenu(
            window
        )

        self.undo_button.setMenu(
            self.undo_history_menu
        )

        self.undo_button.clicked.connect(
            window.undo_operation
        )

        self.undo_button.setEnabled(
            False
        )

        self.toolbar.addWidget(
            self.undo_button
        )

        # ==================================================
        # REDO
        # ==================================================

        self.redo_button = QToolButton(
            window
        )

        self.redo_button.setText(
            "Redo"
        )

        self.redo_button.setToolButtonStyle(
            Qt.ToolButtonTextOnly
        )

        self.redo_button.setPopupMode(
            QToolButton.MenuButtonPopup
        )

        self.redo_history_menu = QMenu(
            window
        )

        self.redo_button.setMenu(
            self.redo_history_menu
        )

        self.redo_button.clicked.connect(
            window.redo_operation
        )

        self.redo_button.setEnabled(
            False
        )

        self.toolbar.addWidget(
            self.redo_button
        )

        # ==================================================
        # VIEW MENU
        # ==================================================

        self.view_menu = (
            window.menuBar()
            .addMenu("View")
        )

        # ----------------------------------
        # Main dataset
        # ----------------------------------

        self.main_dataset_action = QAction(
            "Main Dataset",
            window
        )

        self.main_dataset_action.setCheckable(
            True
        )

        self.main_dataset_action.setChecked(
            True
        )

        # ----------------------------------
        # Result dataset
        # ----------------------------------

        self.result_dataset_action = QAction(
            "Result Dataset",
            window
        )

        self.result_dataset_action.setCheckable(
            True
        )

        self.result_dataset_action.setChecked(
            False
        )

        self.view_menu.addAction(
            self.main_dataset_action
        )

        self.view_menu.addAction(
            self.result_dataset_action
        )


        # ----------------------------------
        # Toolbars
        # ----------------------------------

        self.toolbar_menu = self.view_menu.addMenu(
            "Toolbars"
        )

        self.main_toolbar_action = QAction(
            "Main Toolbar",
            window
        )

        self.main_toolbar_action.setCheckable(
            True
        )

        self.main_toolbar_action.setChecked(
            True
        )

        self.toolbar_menu.addAction(
            self.main_toolbar_action
        )

        self.main_toolbar_action.toggled.connect(
            self.toolbar.setVisible
        )
        # ==================================================
        # CLEAN MENU
        # ==================================================

        self.clean_menu = (
            window.menuBar()
            .addMenu("Clean")
        )

        self.clean_action = QAction(
            "Clean",
            window
        )

        self.clean_menu.addAction(
            self.clean_action
        )

