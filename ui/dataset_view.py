from PySide6.QtWidgets import (
    QStyle,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget
)

from ui.stats.statistics_widget import StatisticsWidget
from ui.graph.graph_tab import GraphTab
from core.dataset_table import DataTable
from ui.menus.selection_toolbar import SelectionToolbar
from PySide6.QtCore import Signal
from ui.model_tab import ModelTab


class DatasetView(QWidget):
    '''Top level container class'''
    close_requested = Signal()
    def __init__(self, title, parent=None):

        super().__init__(parent)

        self.dataframe = None

        # ----------------------------------
        # Components
        # ----------------------------------

        self.table = DataTable()
        self.table.setAlternatingRowColors(True)
        self.selection_toolbar = SelectionToolbar(
            self.table
        )

        self.stats_widget = StatisticsWidget()
        self.model_tab = ModelTab()
        self.graph_tab = GraphTab()

        # ----------------------------------
        # Title
        # ----------------------------------

        title_layout = QHBoxLayout()

        self.title_label = QLabel(title)

        self.close_button = QPushButton()

        self.close_button.setFixedSize(
            30,
            30
        )

        self.close_button.setIcon(
            self.style().standardIcon(
                QStyle.SP_TitleBarCloseButton
            )
        )
        self.close_button.setToolTip(
            "Hide dataset"
        )
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
        model_page = self.model_tab
        self.tabs.addTab(
            model_page,
              "Model"
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
        self.close_button.clicked.connect(
            self.close_requested.emit
        )
            # ======================================
    # DATA
    # ======================================

    def set_dataframe(self, dataframe):

        if dataframe is None:
            self.clear()
            return

        self.dataframe = dataframe.copy()

        self.table.display_dataframe(self.dataframe)

        self.stats_widget.load_dataframe(
            self.dataframe
        )

        self.graph_tab.set_dataframe(
            self.dataframe
        )

        self.model_tab.set_dataframe(
            self.dataframe
        )

    def clear(self):

        self.dataframe = None

        self.table.clearContents()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

        self.stats_widget.load_dataframe(None)
        self.graph_tab.set_dataframe(None)
        self.model_tab.set_dataframe(None)

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

        self.model_tab.set_dataframe(
            dataframe
        )