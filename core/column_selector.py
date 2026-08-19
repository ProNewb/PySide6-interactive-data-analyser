from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QVBoxLayout,
    QWidget
)
from PySide6.QtCore import Qt
import pandas as pd
from PySide6.QtCore import Signal
class ColumnSelector(QWidget):
    selection_changed = Signal()
    def __init__(self, dataframe, parent=None):

        super().__init__(parent)

        self.dataframe = dataframe

        self.layout = QVBoxLayout(self)

        self.checkboxes = []

        self.create_controls()
        self.numeric.stateChanged.connect(
        self.select_numeric_columns
        )

        self.categorical.stateChanged.connect(
            self.select_categorical_columns
        )


    def create_controls(self):

        self.select_all = QCheckBox("Select All")
        self.numeric = QCheckBox("Select Numeric")
        self.categorical = QCheckBox("Select Categorical")

        self.layout.addWidget(self.select_all)
        self.layout.addWidget(self.numeric)
        self.layout.addWidget(self.categorical)

        self.select_all.stateChanged.connect(
            self.select_all_columns
        )

        for column in self.dataframe.columns:

            checkbox = QCheckBox(str(column))
            checkbox.stateChanged.connect(
                self.selection_changed.emit
            )
            self.layout.addWidget(checkbox)

            self.checkboxes.append(
                (column, checkbox)
            )

    def select_all_columns(self, state):

        checked = state == Qt.Checked

        for _, checkbox in self.checkboxes:
            checkbox.setChecked(checked)
        self.selection_changed.emit()

    def get_selected_columns(self):
        """
        Return selected columns.

        If no individual columns are selected, all columns
        are treated as selected.
        """
        selected = [
            column
            for column, checkbox in self.checkboxes
            if checkbox.isChecked()
        ]

        if not selected:
            return list(self.dataframe.columns)

        return selected
    
    def select_numeric_columns(self):

        for column, checkbox in self.checkboxes:

            is_numeric = pd.api.types.is_numeric_dtype(
                self.dataframe[column]
            )

            checkbox.setChecked(is_numeric)
        self.selection_changed.emit()

    def select_categorical_columns(self):

        for column, checkbox in self.checkboxes:

            is_categorical = (
                pd.api.types.is_object_dtype(
                    self.dataframe[column]
                )
                or pd.api.types.is_categorical_dtype(
                    self.dataframe[column]
                )
            )

            checkbox.setChecked(is_categorical)
            self.selection_changed.emit()