from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget
)

from ui.table.dataset_view import DatasetView


class ResultPanel(QWidget):

    result_added = Signal(object)
    result_removed = Signal(object)
    current_changed = Signal(int)
    result_visibility_changed = Signal(bool)

    def __init__(self, workspace=None, parent=None):

        super().__init__(parent)

        self.workspace = workspace

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)

        self.tabs.tabCloseRequested.connect(
            self.remove_result
        )

        self.tabs.currentChanged.connect(
            self._current_changed
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

    # ==================================================
    # CREATE
    # ==================================================

    def add_result(
        self,
        title="Result",
        dataframe=None
    ):

        view = DatasetView(
            title,
            "result",
            workspace=self.workspace,
            parent=self
        )

        if dataframe is not None:
            view.set_dataframe(dataframe)

        index = self.tabs.addTab(
            view,
            title
        )

        self.tabs.setCurrentIndex(index)

        view.close_requested.connect(
            self.hide_results
        )

        self.result_added.emit(view)

        self.show()

        return view

    # ==================================================
    # CURRENT RESULT
    # ==================================================

    def _current_changed(self, index):

        if index >= 0 and self.workspace is not None:

            self.workspace.dataset_manager.set_active_result(
                index
            )

        self.current_changed.emit(index)

    def current_view(self):

        return self.tabs.currentWidget()

    def current_index(self):

        return self.tabs.currentIndex()

    # ==================================================
    # ACCESS
    # ==================================================

    def views(self):

        return [
            self.tabs.widget(i)
            for i in range(self.tabs.count())
        ]

    def view_at(self, index):

        if 0 <= index < self.tabs.count():
            return self.tabs.widget(index)

        return None

    def index_of(self, view):

        return self.tabs.indexOf(view)

    def tab_title(self, index):

        if 0 <= index < self.tabs.count():
            return self.tabs.tabText(index)

        return None

    def has_results(self):

        return self.tabs.count() > 0

    # ==================================================
    # REMOVE
    # ==================================================

    def remove_result(self, index):

        view = self.view_at(index)

        if view is None:
            return

        # Manager owns the data
        self.workspace.dataset_manager.remove_result(
            index
        )

        # UI owns the tab
        self.tabs.removeTab(index)

        self.result_removed.emit(view)

        view.deleteLater()

        if self.tabs.count() == 0:
            self.hide()

    # ==================================================
    # VISIBILITY
    # ==================================================

    def show_result(self, index):

        if not (0 <= index < self.tabs.count()):
            return

        self.tabs.setCurrentIndex(index)
        self.show()


    def hide_results(self):

        self.hide()
        self.result_visibility_changed.emit(False)

    def show_results(self):

        if self.has_results():
            self.show()
            self.result_visibility_changed.emit(True)