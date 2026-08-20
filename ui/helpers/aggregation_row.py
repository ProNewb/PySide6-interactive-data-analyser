from PySide6.QtWidgets import (
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QWidget
)

from PySide6.QtCore import Signal


class AggregationRow(QWidget):
    '''Class resposible for the managment of aggregation rows'''
    remove_requested = Signal(object)

    def __init__(self, dataframe, parent=None):

        super().__init__(parent)

        layout = QHBoxLayout(self)

        self.column_combo = QComboBox()

        for column in dataframe.columns:
            self.column_combo.addItem(
                str(column),
                column
            )

        self.function_combo = QComboBox()

        self.function_combo.addItem(
            "Average",
            "mean"
        )

        self.function_combo.addItem(
            "Minimum",
            "min"
        )

        self.function_combo.addItem(
            "Maximum",
            "max"
        )

        self.function_combo.addItem(
            "Sum",
            "sum"
        )

        self.function_combo.addItem(
            "Count",
            "count"
        )

        self.remove_button = QPushButton("Remove")

        layout.addWidget(self.column_combo)
        layout.addWidget(self.function_combo)
        layout.addWidget(self.remove_button)

        self.remove_button.clicked.connect(
            lambda: self.remove_requested.emit(self) #in line function to emit remove signal on button click
        )

    def get_aggregation(self):

        return (
            self.column_combo.currentData(),
            self.function_combo.currentData()
        )