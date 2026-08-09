from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
    QWidget,
    QLabel,
    QVBoxLayout,
    QTableWidget
)
from PySide6.QtCore import Signal
class DataTable(QTableWidget):
    selection_changed = Signal()
    def __init__(self):
        super().__init__()
        self.dataframe = None
        self.setSortingEnabled(True)

        self.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )

        self.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )


        self.itemSelectionChanged.connect(
            self.selection_changed.emit
        )

    def display_dataframe(self, dataframe):

        # Store pandas dataframe for analysis
        self.dataframe = dataframe.copy()

        self.setRowCount(dataframe.shape[0])
        self.setColumnCount(dataframe.shape[1])

        self.setHorizontalHeaderLabels(
            [str(col) for col in dataframe.columns]
        )

        for row in range(dataframe.shape[0]):
            for col in range(dataframe.shape[1]):

                self.setItem(
                    row,
                    col,
                    QTableWidgetItem(
                        str(dataframe.iat[row, col])
                    )
                )

    def get_selected_columns(self):

        columns = set()

        for item in self.selectedItems():
            columns.add(item.column())

        return list(columns)


    def get_selected_rows(self):

        rows = set()

        for item in self.selectedItems():
            rows.add(item.row())

        return list(rows)


    def get_analysis_dataframe(self):
        

        if self.dataframe is None:
            return None

        print("Stored dataframe:")
        print(self.dataframe)

        rows = self.get_selected_rows()
        columns = self.get_selected_columns()

        print("Selected rows:", rows)
        print("Selected columns:", columns)


        if not rows and not columns:
            return self.dataframe


        if rows and not columns:
            return self.dataframe.iloc[rows, :]


        if columns and not rows:
            return self.dataframe.iloc[:, columns]


        return self.dataframe.iloc[
            rows,
            columns
        ]