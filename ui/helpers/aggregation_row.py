from PySide6.QtWidgets import (
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QWidget
)

from PySide6.QtCore import Signal
import pandas as pd


class AggregationRow(QWidget):
    """Create one aggregation selection row."""

    remove_requested = Signal(object)

    def __init__(self, dataframe, parent=None):

        super().__init__(parent)

        self.dataframe = dataframe
        layout = QHBoxLayout(self)

        self.column_combo = QComboBox()

        for column in dataframe.columns:
            self.column_combo.addItem(
                str(column),
                column
            )

        self.function_combo = QComboBox()
        self.function_combo.addItem("Average", "mean")
        self.function_combo.addItem("Minimum", "min")
        self.function_combo.addItem("Maximum", "max")
        self.function_combo.addItem("Sum", "sum")
        self.function_combo.addItem("Count", "count")

        self.column_combo.currentIndexChanged.connect(
            self.update_function_options
        )
        self.update_function_options()

        self.remove_button = QPushButton("Remove")

        layout.addWidget(self.column_combo)
        layout.addWidget(self.function_combo)
        layout.addWidget(self.remove_button)

        self.remove_button.clicked.connect(
            lambda: self.remove_requested.emit(self)
        )

    def update_function_options(self):
        """Disable functions that are invalid for the selected column."""

        series = self.dataframe[self.column_combo.currentData()]
        numeric = (
            pd.api.types.is_numeric_dtype(series)
            and not pd.api.types.is_bool_dtype(series)
        )

        allowed = {
            "mean": numeric,
            "min": True,
            "max": True,
            "sum": numeric,
            "count": True
        }

        for index in range(self.function_combo.count()):
            function = self.function_combo.itemData(index)
            self.function_combo.model().item(index).setEnabled(
                allowed[function]
            )

        if not allowed[self.function_combo.currentData()]:
            self.function_combo.setCurrentIndex(
                self.function_combo.findData("count")
            )

    def get_aggregation(self):

        return (
            self.column_combo.currentData(),
            self.function_combo.currentData()
        )
