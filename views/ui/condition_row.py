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
from PySide6.QtCore import Signal


    
class ConditionRow(QWidget):
    '''Class responsible for managment of conditional arguments in dialog options'''
    remove_requested = Signal(object)

    def __init__(self, dataframe, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        self.column_combo = QComboBox()
        # convert col names to strings to allow for non alpha numerical names
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
        self.remove_button = QPushButton("Remove")



        layout.addWidget(self.column_combo)
        layout.addWidget(self.operator_combo)
        layout.addWidget(self.value_input)
        layout.addWidget(self.remove_button)
        self.remove_button.clicked.connect(
            lambda: self.remove_requested.emit(self)# inline funct
        )
    def get_condition(self):

        return Condition(
            self.column_combo.currentData(),
            self.operator_combo.currentData(),
            self.value_input.text()
        )

    