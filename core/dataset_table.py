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

class DataTable(QTableWidget):

    def __init__(self):
        super().__init__()

        self.setSortingEnabled(True)

        self.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )

        self.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )


    def display_dataframe(self, dataframe):

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