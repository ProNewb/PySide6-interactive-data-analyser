from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget
)

from views.ui.statistics_widget import StatisticsWidget
from views.ui.graph_tab import GraphTab
from core.dataset_table import DataTable
from views.ui.selection_toolbar import SelectionToolbar
from PySide6.QtCore import Signal

class DatasetView(QWidget):
    close_requested = Signal()
    def __init__(self, title, parent=None):

        super().__init__(parent)

        self.dataframe = None

        # ----------------------------------
        # Components
        # ----------------------------------

        self.table = DataTable()

        self.selection_toolbar = SelectionToolbar(
            self.table
        )

        self.stats_widget = StatisticsWidget()

        self.graph_tab = GraphTab()

        # ----------------------------------
        # Title
        # ----------------------------------

        title_layout = QHBoxLayout()

        self.title_label = QLabel(title)

        self.close_button = QPushButton("×")
        self.close_button.setFixedWidth(30)

        title_layout.addWidget(
            self.title_label
        )

        title_layout.addStretch()

        title_layout.addWidget(
            self.close_button
        )

        # ----------------------------------
        # Tabs
        # ----------------------------------

        self.tabs = QTabWidget()

        # Table
        table_page = QWidget()

        table_layout = QHBoxLayout()

        table_layout.addWidget(
            self.table
        )

        table_layout.addWidget(
            self.selection_toolbar
        )

        table_page.setLayout(
            table_layout
        )

        # Statistics
        statistics_page = QWidget()

        statistics_layout = QVBoxLayout()

        statistics_layout.addWidget(
            self.stats_widget
        )

        statistics_page.setLayout(
            statistics_layout
        )

        # Graphs
        graph_page = self.graph_tab

        self.tabs.addTab(
            table_page,
            "Table"
        )

        self.tabs.addTab(
            statistics_page,
            "Statistics"
        )

        self.tabs.addTab(
            graph_page,
            "Graphs"
        )

        # ----------------------------------
        # Main layout
        # ----------------------------------

        layout = QVBoxLayout()

        layout.addLayout(
            title_layout
        )

        layout.addWidget(
            self.tabs
        )

        self.setLayout(
            layout
        )

        # ----------------------------------
        # Selection
        # ----------------------------------

        self.table.selection_changed.connect(
            self.update_selection
        )

            # ======================================
    # DATA
    # ======================================

    def set_dataframe(self, dataframe):

        self.dataframe = dataframe.copy()

        self.table.display_dataframe(
            self.dataframe
        )

        self.stats_widget.load_dataframe(
            self.dataframe
        )

        self.graph_tab.set_dataframe(
            self.dataframe
        )

    def clear(self):

        self.dataframe = None

        self.table.clearContents()

        self.table.setRowCount(0)
        self.table.setColumnCount(0)



    def get_dataframe(self):

        return self.dataframe

    def get_analysis_dataframe(self):

        return self.table.get_analysis_dataframe()

    def update_selection(self):

        self.update_analysis()


    def update_analysis(self):

        dataframe = self.table.get_analysis_dataframe()

        if dataframe is None:
            return

        self.stats_widget.load_dataframe(
            dataframe
        )

        self.graph_tab.set_dataframe(
            dataframe
        )

        self.close_button.clicked.connect(
            self.close_requested.emit
        )