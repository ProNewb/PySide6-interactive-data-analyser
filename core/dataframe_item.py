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

class DataFrameItem(QTableWidgetItem):

    def __init__(self, value):
        super().__init__(str(value))
        self.value = value

    def __lt__(self, other):

        if isinstance(other, DataFrameItem):

            try:
                return self.value < other.value

            except TypeError:
                return str(self.value) < str(other.value)

        return super().__lt__(other)