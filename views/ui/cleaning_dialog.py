from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QMessageBox,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QWidget
)

from core.column_selector import ColumnSelector
from core.data_clearner import DataCleaner, MissingValueOptions, DuplicateOptions
from core.condition_group import ConditionGroup
from core.conditions import Condition
from core.csv_reader import CSVReader
from core.dataset_table import DataTable
from views.ui.cleaning_stats import CleaningStats
from views.ui.condition_row import ConditionRow
from views.ui.import_dialog import ImportOptions
from views.ui.preview_table import PreviewTable
from analysis.data_summary import DataSummary

class CleaningDialog(QDialog):
    """Dialog for configuring and previewing data-cleaning operations."""

    def __init__(self, dataframe, parent=None):

        super().__init__(parent)
        self.summary = DataSummary()
        self.dataframe = dataframe.copy()
        self.column_selector = ColumnSelector(self.dataframe)
        self.cleaning_stats = CleaningStats()
        self.cleaning_result = None
        self.cleaner = DataCleaner()
        self.setWindowTitle("Clean Data")

        self.build_ui()
        self.connect_signals()
        self.update_operation_ui()
        self.apply_button.clicked.connect(
            self.apply
        )   
        self.column_selector.selection_changed.connect(
            self.update_cleaning_statistics
        )
        self.cleaning_objective_box.currentIndexChanged.connect(
            self.update_operation_ui
        )

    def build_ui(self):

        layout = QVBoxLayout(self)

        # ----------------------------------
        # Cleaning operation
        # ----------------------------------

        layout.addWidget(
            QLabel("Cleaning operation")
        )

        self.cleaning_objective_box = QComboBox()

        self.cleaning_objective_box.addItem(
            "Missing Values",
            "missing"
        )

        self.cleaning_objective_box.addItem(
            "Duplicates",
            "duplicates"
        )

        layout.addWidget(
            self.cleaning_objective_box
        )

        # ----------------------------------
        # Operation controls
        # ----------------------------------

        self.operation_widget = QWidget()

        self.operation_layout = QVBoxLayout(
            self.operation_widget
        )

        layout.addWidget(
            self.operation_widget
        )

        # ----------------------------------
        # Preview
        # ----------------------------------

        layout.addWidget(
            QLabel("Preview")
        )

        self.preview_table = PreviewTable()

        layout.addWidget(
            self.preview_table
        )

        layout.addWidget(
            self.cleaning_stats
        )

        # ----------------------------------
        # Buttons
        # ----------------------------------

        button_layout = QHBoxLayout()

        self.preview_button = QPushButton(
            "Preview Changes"
        )

        self.apply_button = QPushButton(
            "Apply"
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )

        button_layout.addWidget(
            self.preview_button
        )

        button_layout.addStretch()

        button_layout.addWidget(
            self.cancel_button
        )

        button_layout.addWidget(
            self.apply_button
        )

        layout.addLayout(
            button_layout
        )

    def connect_signals(self):

        self.cleaning_objective_box.currentIndexChanged.connect(
            self.update_operation_ui
        )

        self.preview_button.clicked.connect(
            self.update_preview
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

    def update_operation_ui(self):

        self.clear_operation_ui()

        operation = (
            self.cleaning_objective_box.currentData()
        )

        if operation == "missing":

            self.missing_val_operations()

        elif operation == "duplicates":

            self.duplicate_operations()

        self.update_cleaning_statistics()

    def update_preview(self):

        operation = self.get_operation()

        if operation is None:
            return

        try:

            if isinstance(operation, MissingValueOptions):
                self.cleaning_result = self.cleaner.clean_missing(
                    self.dataframe,
                    operation
                )
            else:
                self.cleaning_result = self.cleaner.remove_duplicates(
                    self.dataframe,
                    operation
                )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Cleaning Error",
                str(error)
            )

            return

        self.preview_table.display_dataframe(
            self.cleaning_result
        )

        self.update_cleaning_statistics()

        self.preview_table.display_dataframe(
            self.cleaning_result
        )

    def duplicate_operations(self):
        self.operation_layout.addWidget(
            QLabel("Duplicates")
        )
        self.groupBy()
        self.col_sel()
        self.action()
        self.fill()

    def missing_val_operations(self):

        self.operation_layout.addWidget(
            QLabel("Missing Values")
        )
        self.col_sel()
        self.action()
        self.fill()

    def groupBy(self):
        """
        Creates a checkbox for each column in self.dataframe
        and stores them in self.dupe_cols for later use.
        Adds them directly to self.operation_layout.
        """
        self.dupe_cols = []
        self.checkbox_group = QButtonGroup(self)
        self.checkbox_group.setExclusive(False)  # Allow multiple selections

        # Add checkboxes directly to the existing operation_layout
        for col in self.dataframe.columns:
            cb = QCheckBox(str(col), self)
            self.checkbox_group.addButton(cb)
            self.operation_layout.addWidget(cb)  
            self.dupe_cols.append((col, cb))
            cb.stateChanged.connect(
                self.update_cleaning_statistics
            )
            
    def col_sel(self):
        # -------------------------------
        # Column selection
        # -------------------------------

        self.operation_layout.addWidget(
            QLabel("Columns")
        )

        self.missing_column_combo = QComboBox()

        self.missing_column_combo.addItem(
            "All Columns",
            None
        )
        self.missing_column_combo.addItem(
            "All numerical Columns",
            None
        )
        self.missing_column_combo.addItem(
            "All categorical Columns",
            None
        )

        for column in self.dataframe.columns:

            self.missing_column_combo.addItem(
                str(column),
                column
            )

        self.operation_layout.addWidget(
            self.missing_column_combo
        )
        self.missing_column_combo.currentIndexChanged.connect(
            self.update_cleaning_statistics
        )
    def action(self):
        # -------------------------------
        # Action
        # -------------------------------

        self.operation_layout.addWidget(
            QLabel("Action")
        )

        self.missing_action_combo = QComboBox()

        self.missing_action_combo.addItem(
            "Drop rows",
            "drop"
        )

        self.missing_action_combo.addItem(
            "Fill values",
            "fill"
        )

        self.operation_layout.addWidget(
            self.missing_action_combo
        )
        self.missing_action_combo.currentIndexChanged.connect(
            self.update_cleaning_statistics
        )
    def fill(self):
        # -------------------------------
        # Fill method
        # -------------------------------

        self.fill_method_combo = QComboBox()

        self.fill_method_combo.addItem(
            "Mean",
            "mean"
        )

        self.fill_method_combo.addItem(
            "Median",
            "median"
        )

        self.fill_method_combo.addItem(
            "Mode",
            "mode"
        )

        self.fill_method_combo.addItem(
            "Constant",
            "constant"
        )

        self.fill_method_combo.addItem(
            "NaN",
            "nan"
        )

        self.operation_layout.addWidget(
            QLabel("Fill method")
        )

        self.operation_layout.addWidget(
            self.fill_method_combo
        )

        # -------------------------------
        # Constant value
        # -------------------------------

        self.fill_value = QLineEdit()

        self.fill_value.setPlaceholderText(
            "Enter value"
        )

        self.operation_layout.addWidget(
            self.fill_value
        )

        self.fill_method_combo.currentIndexChanged.connect(
            self.update_fill_controls
        )
        self.fill_method_combo.currentIndexChanged.connect(
            self.update_cleaning_statistics
        )

        self.missing_action_combo.currentIndexChanged.connect(
            self.update_fill_controls
        )

        self.update_fill_controls()


    def clear_operation_ui(self):

        while self.operation_layout.count():

            item = self.operation_layout.takeAt(0)

            if item.widget():

                item.widget().deleteLater()

            elif item.layout():

                self.clear_layout(item.layout())

    def clear_layout(self, layout):

        while layout.count():

            item = layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

            elif item.layout():
                self.clear_layout(item.layout())
                

    def update_fill_controls(self):

        is_fill = (
            self.missing_action_combo.currentData()
            == "fill"
        )

        self.fill_method_combo.setVisible(is_fill)

        self.fill_value.setVisible(
            is_fill
            and self.fill_method_combo.currentData()
            == "constant"
        )

    def get_result(self):

        return self.cleaning_result


    def get_operation(self):

        operation = (
            self.cleaning_objective_box
            .currentData()
        )

        if operation == "duplicates":
            columns = [
                column
                for column, checkbox in self.dupe_cols
                if checkbox.isChecked()
            ]

            return DuplicateOptions(columns=columns)

        if operation == "missing":

            columns = (
                self.column_selector
                .get_selected_columns()
            )

            action = (
                self.missing_action_combo
                .currentData()
            )

            method = None
            value = None

            if action == "fill":

                method = (
                    self.fill_method_combo
                    .currentData()
                )

                if method == "constant":
                    value = self.fill_value.text()

            return MissingValueOptions(
                columns=columns,
                action=action,
                method=method,
                value=value
            )

        return None


    def apply(self):

        self.update_preview()

        if self.cleaning_result is None:
            return

        self.accept()

    def get_result(self):

        return self.cleaning_result

    def missing_stats(self):
        pass
    def duplicate_stats(self):
        pass

    def update_statistics(
        self,
        dataframe,
        selected_columns=None
    ):

        summary = self.summary.generate(
            dataframe
        )

        self.rows_label.setText(
            f"Rows: {summary['rows']}"
        )

        self.columns_label.setText(
            f"Columns: {summary['columns']}"
        )

    def update_cleaning_statistics(self):

        operation = (
            self.cleaning_objective_box.currentData()
        )

        if operation == "missing":
            columns = self.column_selector.get_selected_columns()
            selected_operation = self.get_operation()
            result = self.cleaner.clean_missing(
                self.dataframe,
                selected_operation
            )
            self.cleaning_stats.update_comparison(
                self.dataframe,
                result,
                columns,
                "missing"
            )

        elif operation == "duplicates":
            columns = [
                column
                for column, checkbox in self.dupe_cols
                if checkbox.isChecked()
            ] or list(self.dataframe.columns)
            result = self.cleaner.remove_duplicates(
                self.dataframe,
                DuplicateOptions(columns=columns)
            )
            self.cleaning_stats.update_comparison(
                self.dataframe,
                result,
                columns,
                "duplicates"
            )