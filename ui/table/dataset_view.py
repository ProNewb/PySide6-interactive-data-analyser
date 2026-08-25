from PySide6.QtWidgets import (
    QMenu,
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
from PySide6.QtCore import Qt, Signal
from ui.model_tab import ModelTab


class DatasetView(QWidget):

    close_requested = Signal()

    # Data operations
    filter_requested = Signal()
    transform_requested = Signal()
    aggregate_requested = Signal()
    join_requested = Signal()
    clean_requested = Signal()

    # Column operations
    rename_column_requested = Signal(object)
    duplicate_column_requested = Signal(object)
    add_column_requested = Signal()
    delete_column_requested = Signal(object)
    calculated_column_requested = Signal()
    calculated_column_requested = Signal(object)
    # Row operations
    add_row_requested = Signal()
    duplicate_row_requested = Signal(object)
    delete_row_requested = Signal(object)

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

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(
            self.show_context_menu
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

    def show_context_menu(self, pos):

        index = self.table.indexAt(pos)

        if not index.isValid():
            return

        row_position = index.row()
        column_position = index.column()

        column_name = self.table.model().headerData(
            column_position,
            Qt.Horizontal,
            Qt.DisplayRole
        )

        row_index = self.dataframe.index[row_position]

        menu = QMenu(self)

        # -----------------------------
        # Clipboard
        # -----------------------------

        copy_action = menu.addAction("Copy")

        menu.addSeparator()

        # -----------------------------
        # Edit
        # -----------------------------

        edit_menu = menu.addMenu("Edit")

        column_menu = edit_menu.addMenu("Column")

        rename_column = column_menu.addAction("Rename")
        duplicate_column = column_menu.addAction("Duplicate column")
        add_column = column_menu.addAction("Add column")
        calculated_column = column_menu.addAction(
            "Calculated column"
        )
        delete_column = column_menu.addAction("Delete column")

        row_menu = edit_menu.addMenu("Row")

        add_row = row_menu.addAction("Add row")
        duplicate_row = row_menu.addAction("Duplicate row")
        delete_row = row_menu.addAction("Delete row")

        # -----------------------------
        # Data operations
        # -----------------------------

        menu.addSeparator()

        filter_action = menu.addAction("Filter")
        aggregate_action = menu.addAction("Aggregate")
        transform_action = menu.addAction("Transform")
        join_action = menu.addAction("Join")
        clean_action = menu.addAction("Clean")

        menu.addSeparator()

        clear_action = menu.addAction("Clear Selection")

        action = menu.exec(
            self.table.viewport().mapToGlobal(pos)
        )

        if action == copy_action:
            self.table.copy_selection()

        elif action == rename_column:
            self.rename_column_requested.emit(self, column_name)

        elif action == duplicate_column:
            self.duplicate_column_requested.emit(column_name)

        elif action == add_column:
            self.add_column_requested.emit()

        elif action == calculated_column:
            self.calculated_column_requested.emit(self)

        elif action == delete_column:
            self.delete_column_requested.emit(column_name)

        elif action == add_row:
            self.add_row_requested.emit()

        elif action == duplicate_row:
            self.duplicate_row_requested.emit(row_index)

        elif action == delete_row:
            self.delete_row_requested.emit(self, row_index)

        elif action == filter_action:
            self.filter_requested.emit()

        elif action == aggregate_action:
            self.aggregate_requested.emit()

        elif action == transform_action:
            self.transform_requested.emit()

        elif action == join_action:
            self.join_requested.emit()

        elif action == clean_action:
            self.clean_requested.emit()
              
        elif action == clear_action:
            self.table.clearSelection()

    def selected_column(self):

        columns = self.get_selected_columns()

        if len(columns) != 1:
            return None

        return self.dataframe.columns[columns[0]]


    def selected_columns(self):

        return [
            self.dataframe.columns[i]
            for i in self.get_selected_columns()
        ]


    def selected_rows(self):
        """Return dataframe index values, not table positions."""

        rows = self.get_selected_rows()

        return [
            self.dataframe.index[i]
            for i in rows
    ]