from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QSplitter
)
from PySide6.QtCore import Qt

from core.condition_group import ConditionGroup
from core.conditions import Condition
from core.dataset_table import DataTable
from ui.helpers.condition_row import ConditionRow
from ui.dialogs.import_dialog import ImportOptions
from ui.table.preview_table import PreviewTable



class DataDialog(QDialog):
    ''' Class responsible for displaying and capturing user options for aggregation and filtering'''
    def __init__(self, dataframe, parent=None, target_dataframes=None,
                 target="main"):

        super().__init__(parent)

        self.dataframe = dataframe
        self.target_dataframes = target_dataframes or {target: dataframe}
        self.condition_rows = []
        self.preview_table = PreviewTable()
        self.filtered_preview_table = PreviewTable()
       
        self.options = ImportOptions()
        self.datatable = DataTable()
        self.setWindowTitle("Filter Data")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Target dataset"))
        self.target_combo = QComboBox()
        for key, label in (("main", "Main Dataset"),
                           ("result", "Result Dataset")):
            if key in self.target_dataframes:
                self.target_combo.addItem(label, key)
        self.target_combo.setCurrentIndex(
            max(0, self.target_combo.findData(target))
        )
        layout.addWidget(self.target_combo)
        self.target_combo.currentIndexChanged.connect(
            self.change_target
        )

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

        preview_splitter = QSplitter(Qt.Horizontal)
        preview_splitter.addWidget(self.preview_table)
        preview_splitter.addWidget(self.filtered_preview_table)
        layout.addWidget(preview_splitter)

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
            self.accept_dialog
        )

        self.setLayout(layout)

        # --------------------------------
        # Create first condition
        # --------------------------------

        self.change_target()
        self.update_preview()


    def get_conditions(self):

        conditions = [
            row.get_condition()
            for row in self.condition_rows
        ]

        return ConditionGroup(
            conditions,
            self.logic_combo.currentData()
        )

    def get_target(self):
        return self.target_combo.currentData()

    def change_target(self):
        if not hasattr(self, "conditions_layout"):
            return
        self.dataframe = self.target_dataframes[self.get_target()]
        while self.conditions_layout.count():
            item = self.conditions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.condition_rows.clear()
        self.create_new_condition()
        self.update_preview()

    def create_new_condition(self):

        row = ConditionRow(self.dataframe)

        row.remove_requested.connect(
            self.remove_condition
        )

        self.conditions_layout.addWidget(row)

        self.condition_rows.append(row)
        row.column_combo.currentIndexChanged.connect(self.update_preview)
        row.operator_combo.currentIndexChanged.connect(self.update_preview)
        row.value_input.textChanged.connect(self.update_preview)


    def remove_condition(self, row):

        if len(self.condition_rows) <= 1:
            return

        self.condition_rows.remove(row)

        self.conditions_layout.removeWidget(row)

        row.deleteLater()
        self.update_preview()

    def update_preview(self):
        self.preview_table.display_dataframe(self.dataframe)
        try:
            filtered = self.dataframe[
                self.get_conditions().evaluate(self.dataframe)
            ]
        except (KeyError, TypeError, ValueError):
            self.filtered_preview_table.clearContents()
            self.filtered_preview_table.setRowCount(0)
            self.apply_button.setEnabled(False)
            return

        self.filtered_preview_table.display_dataframe(filtered)
        self.apply_button.setEnabled(True)

    def accept_dialog(self):
        self.update_preview()
        if self.apply_button.isEnabled():
            self.accept()