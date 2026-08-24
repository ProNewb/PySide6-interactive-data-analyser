from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter
)

from core.dataset_manager import DatasetManager
from ui.dataset_view import DatasetView
from controllers.file_controller import FileController
from PySide6.QtCore import Qt, QFileInfo

class Workspace(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.dataset_manager = DatasetManager()

        self.file_controller = FileController(
            self.dataset_manager
        )

        self.main_view = DatasetView(
            "Main Dataset"
        )

        self.result_view = DatasetView(
            "Result Dataset"
        )

        self.result_view.hide()

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

        self.refresh()

    # ======================================
    # REFRESH
    # ======================================

    def refresh(self):

        self.update_views()
        self.update_comparison_layout()

    # ======================================
    # VIEWS
    # ======================================

    def update_views(self):

        main = self.dataset_manager.get_dataframe()
        result = self.dataset_manager.get_result_dataframe()

        if main is not None:
            self.main_view.set_dataframe(main)
        else:
            self.main_view.clear()

        if result is not None:
            self.result_view.set_dataframe(result)
        else:
            self.result_view.clear()

        self.update_comparison_layout()

    # ======================================
    # LAYOUT
    # ======================================

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