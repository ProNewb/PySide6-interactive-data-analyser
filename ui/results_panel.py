from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
)

from ui.table.dataset_view import DatasetView


class ResultPanel(QWidget):

    result_added = Signal(object)
    result_removed = Signal(object)
    #close_requested = Signal()

    def __init__(self, workspace=None, parent=None):
        super().__init__(parent)

        self.workspace = workspace

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)

        self.tabs.tabCloseRequested.connect(
            self.remove_result
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

    # ==================================================
    # RESULTS
    # ==================================================

    def add_result(self, title="Result", dataframe=None):

        view = DatasetView(
            title,
            "result",
            workspace=self.workspace,
            parent=self
        )

        index = self.tabs.addTab(
            view,
            title
        )

        self.tabs.setCurrentIndex(index)

        view.close_requested.connect(
            lambda view=view: self.close_view(view)
        )

        if dataframe is not None:
            view.set_dataframe(dataframe)

        self.result_added.emit(view)

        return view

    def current_view(self):
        return self.tabs.currentWidget()

    def current_index(self):
        return self.tabs.currentIndex()

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

    def current_dataframe(self):

        view = self.current_view()

        if view is None:
            return None

        return view.get_dataframe()

    def has_results(self):
        return self.tabs.count() > 0

    # ==================================================
    # CLOSE
    # ==================================================

    def close_view(self, view):

        index = self.tabs.indexOf(view)

        if index >= 0:
            self.remove_result(index)

    def remove_result(self, index):

        view = self.tabs.widget(index)

        if view is None:
            return

        self.tabs.removeTab(index)

        self.result_removed.emit(view)

        view.deleteLater()

        if self.tabs.count() == 0:
            self.hide()
            

    # ==================================================
    # VISIBILITY
    # ==================================================

    def show_results(self):
        self.show()

    def hide_results(self):
        self.hide()

    def show_result(self, index):

        view = self.view_at(index)

        if view is None:
            return

        self.tabs.setCurrentIndex(index)
        self.show()

    def tab_title(self, index):

        if 0 <= index < self.tabs.count():
            return self.tabs.tabText(index)

        return None