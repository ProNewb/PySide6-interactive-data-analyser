from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter
)

from core.dataset_manager import DatasetManager
from ui.dataset_view import DatasetView
from controllers.file_controller import FileController

class Workspace(QWidget):
    """Container for one open dataset/project."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # ----------------------------------
        # Workspace data
        # ----------------------------------

        self.dataset_manager = DatasetManager()
        self.file_controller = FileController(
            self.dataset_manager
)
        # ----------------------------------
        # Dataset views
        # ----------------------------------

        self.main_view = DatasetView(
            "Main Dataset"
        )

        self.result_view = DatasetView(
            "Result Dataset"
        )

        self.result_view.hide()

        # ----------------------------------
        # Layout
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

        layout = QVBoxLayout(self)

        layout.addWidget(
            self.splitter
        )

        self.update_views()

    # ======================================
    # DATA
    # ======================================

    def refresh(self):

        self.update_views()

    def update_views(self):

        main = self.dataset_manager.get_dataframe()
        result = self.dataset_manager.get_result_dataframe()

        # Main
        if main is not None:
            self.main_view.set_dataframe(main)
        else:
            self.main_view.clear()

        # Result
        if result is not None:
            self.result_view.set_dataframe(result)
        else:
            self.result_view.clear()

        self.main_view.setVisible(
            main is not None
        )

        self.result_view.setVisible(
            result is not None
        )

    # ======================================
    # DATA ACCESS
    # ======================================

    def get_main_dataframe(self):
        return self.dataset_manager.get_dataframe()

    def get_result_dataframe(self):
        return self.dataset_manager.get_result_dataframe()

    def has_data(self):
        return self.dataset_manager.has_data()

    def has_result(self):
        return self.dataset_manager.has_result()

    # ======================================
    # FILE
    # ======================================

    def filename(self):
        return self.dataset_manager.filename

    def update_comparison_layout(self):

        main_available = (
            self.dataset_manager.get_dataframe()
            is not None
        )

        result_available = (
            self.dataset_manager.get_result_dataframe()
            is not None
        )

        self.main_view.setVisible(
            main_available
        )

        self.result_view.setVisible(
            result_available
        )

        if main_available and result_available:

            self.splitter.setSizes([
                600,
                600
            ])

        elif main_available:

            self.splitter.setSizes([
                1200,
                0
            ])

        elif result_available:

            self.splitter.setSizes([
                0,
                1200
            ])

    def refresh(self):

        self.update_views()
        self.update_comparison_layout()