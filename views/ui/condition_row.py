from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QWidget
)

from core.conditions import Condition
class ConditionRow(QWidget):

    def __init__(self, dataframe, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        self.column_combo = QComboBox()

        for column in dataframe.columns:
            self.column_combo.addItem(
                str(column),
                column
            )

        self.operator_combo = QComboBox()

        self.operator_combo.addItem(
            "Equals",
            "equals"
        )

        self.operator_combo.addItem(
            "Not equal",
            "not_equals"
        )

        self.operator_combo.addItem(
            "Contains",
            "contains"
        )

        self.operator_combo.addItem(
            "Greater than",
            "greater_than"
        )

        self.operator_combo.addItem(
            "Less than",
            "less_than"
        )

        self.operator_combo.addItem(
            "Greater or equal",
            "greater_or_equal"
        )

        self.operator_combo.addItem(
            "Less or equal",
            "less_or_equal"
        )

        self.value_input = QLineEdit()

        layout.addWidget(self.column_combo)
        layout.addWidget(self.operator_combo)
        layout.addWidget(self.value_input)

    def get_condition(self):

        return Condition(
            self.column_combo.currentData(),
            self.operator_combo.currentData(),
            self.value_input.text()
        )