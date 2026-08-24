from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QMessageBox,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QWidget
)

from PySide6.QtCore import Qt

from core.column_selector import ColumnSelector
from core.data_clearner import DataCleaner, MissingValueOptions, DuplicateOptions
from core.condition_group import ConditionGroup
from core.conditions import Condition
from core.csv_reader import CSVReader
from core.dataset_table import DataTable
from ui.stats.cleaning_stats import CleaningStats
from ui.helpers.condition_row import ConditionRow
from ui.dialogs.import_dialog import ImportOptions
from ui.table.preview_table import PreviewTable
from analysis.data_summary import DataSummary

class CleaningDialog(QDialog):
    """Dialog for configuring and previewing data-cleaning operations."""

    def __init__(self, dataframe, parent=None, target_dataframes=None,
                 target="main"):
        super().__init__(parent)
        self.summary = DataSummary()
        self.dataframe = dataframe.copy()
        self.column_selector = ColumnSelector(self.dataframe)
        self.cleaning_stats = CleaningStats()
        self.cleaning_result = None
        self.cleaner = DataCleaner()
        self.setWindowTitle("Clean Data")
        self.resize(1600, 900)
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

        outer_layout = QVBoxLayout(self)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        self.dialog_scroll = QScrollArea()
        self.dialog_scroll.setWidgetResizable(True)
        self.dialog_scroll.setWidget(content_widget)
        outer_layout.addWidget(self.dialog_scroll)

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

        self.operation_scroll = QScrollArea()
        self.operation_scroll.setWidgetResizable(True)
        self.operation_scroll.setMinimumHeight(240)
        self.operation_scroll.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.operation_scroll.setWidget(self.operation_widget)
        layout.addWidget(self.operation_scroll)

        # ----------------------------------
        # Preview
        # ----------------------------------

        layout.addWidget(
            QLabel("Preview")
        )

        self.before_preview = PreviewTable()
        self.after_preview = PreviewTable()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.before_preview)
        splitter.addWidget(self.after_preview)

        layout.addWidget(splitter)

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

        self.before_preview.display_dataframe(self.dataframe)

        operation = self.get_operation()

        if isinstance(operation, MissingValueOptions):
            result = self.cleaner.clean_missing(
                self.dataframe,
                operation
            )
        else:
            result = self.cleaner.remove_duplicates(
                self.dataframe,
                operation
            )

        self.cleaning_result = result

        self.after_preview.display_dataframe(result)

    def duplicate_operations(self):
        self.operation_layout.addWidget(
            QLabel("Duplicates")
        )
        self.duplicate_selection_widget = QWidget()
        self.duplicate_selection_layout = QVBoxLayout(
            self.duplicate_selection_widget
        )
        self.duplicate_selection_layout.setContentsMargins(0, 0, 0, 0)

        self.duplicate_scroll = QScrollArea()
        self.duplicate_scroll.setWidgetResizable(True)
        self.duplicate_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.duplicate_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.duplicate_scroll.setMinimumHeight(220)
        self.duplicate_scroll.setWidget(self.duplicate_selection_widget)
        self.operation_layout.addWidget(self.duplicate_scroll)
        self.groupBy(self.duplicate_selection_layout)
        self.action()
        self.fill()

    def missing_val_operations(self):

        self.operation_layout.addWidget(
            QLabel("Missing Values")
        )
        self.col_sel()
        self.action()
        self.fill()

    def groupBy(self, target_layout):
        """
        Creates a checkbox for each column in self.dataframe
        and stores them in self.dupe_cols for later use.
        Adds them directly to self.operation_layout.
        """
        self.dupe_cols = []
        self.checkbox_group = QButtonGroup(self)
        self.checkbox_group.setExclusive(False)  # Allow multiple selections

        target_layout.addWidget(
            QLabel("Columns")
        )

        self.duplicate_preset_checkboxes = []
        preset_layout = QGridLayout()
        presets_per_row = 3
        for label, preset in (
            ("All Columns", "all"),
            ("All Numeric", "numeric"),
            ("All Datetime", "datetime"),
            ("All Categorical", "categorical"),
            ("Location / Coordinates", "location")
        ):
            preset_checkbox = QCheckBox(label, self)
            preset_checkbox.clicked.connect(
                lambda checked, value=preset:
                    self.update_duplicate_preset(checked, value)
            )
            preset_index = len(self.duplicate_preset_checkboxes)
            preset_layout.addWidget(
                preset_checkbox,
                preset_index // presets_per_row,
                preset_index % presets_per_row
            )
            self.duplicate_preset_checkboxes.append(preset_checkbox)

        for column_index in range(presets_per_row):
            preset_layout.setColumnStretch(column_index, 1)

        target_layout.addLayout(preset_layout)

        column_layout = QGridLayout()
        columns_per_row = 3

        for column_index in range(columns_per_row):
            column_layout.setColumnStretch(column_index, 1)

        # Add checkboxes directly to the existing operation_layout
        for index, col in enumerate(self.dataframe.columns):
            cb = QCheckBox(str(col), self)
            self.checkbox_group.addButton(cb)
            column_layout.addWidget(
                cb,
                index // columns_per_row,
                index % columns_per_row
            )
            self.dupe_cols.append((col, cb))
            cb.stateChanged.connect(
                self.update_cleaning_statistics
            )

        target_layout.addLayout(column_layout)

    def add_column_presets(self, combo):
        combo.addItem("All Columns", "all")
        combo.addItem("All Numeric", "numeric")
        combo.addItem("All Datetime", "datetime")
        combo.addItem("All Categorical", "categorical")
        combo.addItem("Location / Coordinates", "location")

        for column in self.dataframe.columns:
            combo.addItem(str(column), [column])

    def selected_preset_columns(self, preset):
        if preset == "all":
            return list(self.dataframe.columns)

        if preset == "numeric":
            return list(
                self.dataframe.select_dtypes(include="number").columns
            )

        if preset == "datetime":
            return list(
                self.dataframe.select_dtypes(
                    include=["datetime", "datetimetz"]
                ).columns
            )

        if preset == "categorical":
            return list(
                self.dataframe.select_dtypes(
                    include=["object", "category", "string"]
                ).columns
            )

        if preset == "location":
            location_names = {
                "lat", "latitude", "lon", "lng", "longitude",
                "x", "y", "easting", "northing"
            }
            return [
                column
                for column in self.dataframe.columns
                if str(column).strip().lower() in location_names
            ]

        return list(preset or [])

    def update_duplicate_preset(self, checked, preset):
        if not checked:
            self.update_cleaning_statistics()
            return

        for preset_checkbox in self.duplicate_preset_checkboxes:
            if preset_checkbox is not self.sender():
                preset_checkbox.blockSignals(True)
                preset_checkbox.setChecked(False)
                preset_checkbox.blockSignals(False)

        self.apply_duplicate_preset(preset)

    def apply_duplicate_preset(self, preset):
        if not hasattr(self, "dupe_cols"):
            return

        columns = self.selected_preset_columns(preset)

        for column, checkbox in self.dupe_cols:
            checkbox.blockSignals(True)
            checkbox.setChecked(column in columns)
            checkbox.blockSignals(False)

        self.update_cleaning_statistics()
            
    def col_sel(self):
        # -------------------------------
        # Column selection
        # -------------------------------

        self.operation_layout.addWidget(
            QLabel("Columns")
        )

        self.missing_column_combo = QComboBox()

        self.add_column_presets(self.missing_column_combo)

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
        self.fill_value.textChanged.connect(
            self.update_cleaning_statistics
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

            columns = self.selected_preset_columns(
                self.missing_column_combo.currentData()
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
        """Refresh compatibility statistics for a missing-value operation."""
        self.update_cleaning_statistics()

    def duplicate_stats(self):
        """Refresh compatibility statistics for a duplicate operation."""
        self.update_cleaning_statistics()

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
            columns = self.selected_preset_columns(
                self.missing_column_combo.currentData()
            )
            selected_operation = self.get_operation()
            try:
                result = self.cleaner.clean_missing(
                    self.dataframe,
                    selected_operation
                )
            except ValueError as error:
                self.cleaning_stats.show_error(str(error))
                return
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
    def set_dataframe(self, dataframe):
        self.dataframe = dataframe.copy()
        self.update_preview()