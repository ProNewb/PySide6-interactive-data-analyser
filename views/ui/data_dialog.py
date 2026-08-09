from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton
)

from core.condition_group import ConditionGroup
from core.conditions import Condition
from views.ui.condition_row import ConditionRow



class DataDialog(QDialog):

    def __init__(self, dataframe, parent=None):

        super().__init__(parent)

        self.dataframe = dataframe
        self.condition_rows = []

        self.setWindowTitle("Filter Data")

        layout = QVBoxLayout()

        # --------------------------------
        # Conditions
        # --------------------------------

        layout.addWidget(
            QLabel("Conditions")
        )

        self.conditions_layout = QVBoxLayout()

        layout.addLayout(
            self.conditions_layout
        )

        # --------------------------------
        # Add condition
        # --------------------------------

        self.new_condition = QPushButton(
            "+ Add Condition"
        )

        layout.addWidget(
            self.new_condition
        )

        self.new_condition.clicked.connect(
            self.create_new_condition
        )

        # --------------------------------
        # Logic
        # --------------------------------

        layout.addWidget(
            QLabel("Match conditions using")
        )

        self.logic_combo = QComboBox()

        self.logic_combo.addItem(
            "AND",
            "AND"
        )

        self.logic_combo.addItem(
            "OR",
            "OR"
        )

        layout.addWidget(
            self.logic_combo
        )

        # --------------------------------
        # Apply
        # --------------------------------

        self.apply_button = QPushButton(
            "Apply"
        )

        layout.addWidget(
            self.apply_button
        )

        self.apply_button.clicked.connect(
            self.accept
        )

        self.setLayout(layout)

        # --------------------------------
        # Create first condition
        # --------------------------------

        self.create_new_condition()

    def create_new_condition(self):

        row = ConditionRow(
            self.dataframe
        )

        self.conditions_layout.addWidget(
            row
        )

        self.condition_rows.append(
            row
        )

    def get_conditions(self):

        conditions = [
            row.get_condition()
            for row in self.condition_rows
        ]

        return ConditionGroup(
            conditions,
            self.logic_combo.currentData()
        )