from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QTableWidget,
    QTableWidgetItem
)

from core.dataframe_item import DataFrameItem


class DataTable(QTableWidget):
    """Table widget used to display and select rows from a DataFrame."""

    selection_changed = Signal()

    def __init__(self):
        super().__init__()

        # DataFrame currently displayed by the table.
        self.dataframe = None

        # Allow the user to sort columns by clicking the headers.
        self.setSortingEnabled(True)

        # Allow multiple rows to be selected.
        self.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )

        # Selecting a cell selects the entire row.
        self.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        # Notify the parent view whenever the selection changes.
        self.itemSelectionChanged.connect(
            self.selection_changed.emit
        )

    # ==================================================
    # DISPLAY
    # ==================================================

    def display_dataframe(self, dataframe):
        """Display a DataFrame in the table."""

        if dataframe is None:
            self.clear()
            self.dataframe = None
            return

        # Sorting is temporarily disabled while populating
        # the table to avoid unnecessary sorting operations.
        was_sorting_enabled = self.isSortingEnabled()
        self.setSortingEnabled(False)

        self.clearContents()

        # Store our own copy so the table always has a
        # consistent representation of the displayed data.
        self.dataframe = dataframe.copy()

        self.setRowCount(
            dataframe.shape[0]
        )

        self.setColumnCount(
            dataframe.shape[1]
        )

        self.setHorizontalHeaderLabels(
            [str(column) for column in dataframe.columns]
        )

        # Populate the table.
        for row in range(dataframe.shape[0]):

            for column in range(dataframe.shape[1]):

                value = dataframe.iat[row, column]

                self.setItem(
                    row,
                    column,
                    DataFrameItem(value)
                )

        # Restore the previous sorting state.
        self.setSortingEnabled(
            was_sorting_enabled
        )

    # ==================================================
    # SELECTION
    # ==================================================

    def get_selected_rows(self):
        """Return the indexes of all currently selected rows."""

        return list({
            item.row()
            for item in self.selectedItems()
        })

    def get_selected_columns(self):
        """Return the indexes of all currently selected columns."""

        return list({
            item.column()
            for item in self.selectedItems()
        })

    def get_analysis_dataframe(self):
        """
        Return the portion of the DataFrame selected by the user.

        If nothing is selected, return the complete DataFrame.
        """

        if self.dataframe is None:
            return None

        rows = self.get_selected_rows()
        columns = self.get_selected_columns()

        # Nothing selected -> analyse the complete dataset.
        if not rows and not columns:
            return self.dataframe

        # Rows selected -> analyse those rows.
        if rows and not columns:
            return self.dataframe.iloc[rows, :]

        # Columns selected -> analyse those columns.
        if columns and not rows:
            return self.dataframe.iloc[:, columns]

        # Both rows and columns selected.
        return self.dataframe.iloc[
            rows,
            columns
        ]