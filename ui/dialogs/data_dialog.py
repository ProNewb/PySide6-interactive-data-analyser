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
from core.dataset_table import DataTable
from ui.helpers.condition_row import ConditionRow
from ui.dialogs.import_dialog import ImportOptions
from ui.table.preview_table import PreviewTable



class DataDialog(QDialog):
    ''' Class responsible for displaying and capturing user options for aggregation and filtering'''
    def __init__(self, dataframe, parent=None):

        super().__init__(parent)

        self.dataframe = dataframe
        self.condition_rows = []
        self.preview_table = PreviewTable()
       
        self.options = ImportOptions()
        self.datatable = DataTable()
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


    def get_conditions(self):

        conditions = [
            row.get_condition()
            for row in self.condition_rows
        ]

        return ConditionGroup(
            conditions,
            self.logic_combo.currentData()
        )

    def create_new_condition(self):

        row = ConditionRow(self.dataframe)

        row.remove_requested.connect(
            self.remove_condition
        )

        self.conditions_layout.addWidget(row)

        self.condition_rows.append(row)


    def remove_condition(self, row):

        if len(self.condition_rows) <= 1:
            return

        self.condition_rows.remove(row)

        self.conditions_layout.removeWidget(row)

        row.deleteLater()