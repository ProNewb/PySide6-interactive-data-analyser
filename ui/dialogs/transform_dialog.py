from PySide6.QtCore import Qt
import pandas as pd
from PySide6.QtWidgets import (
    QComboBox,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QMenu,
)
from PySide6.QtGui import QAction
from core.data_processor import DataProcessor, DataType, TransformConfig
from ui.table.preview_table import PreviewTable


class TransformDialog(QDialog):
    """Configure a column transform and preview its result."""

    def __init__(
        self,
        datasets,
        parent=None,
        current=None,
        use_selection=False
    ):
        super().__init__(parent)
        self.datasets = datasets
        self.preview = PreviewTable()
        self.result_preview = PreviewTable()
        self.operation = None
        self.setWindowTitle("Transform Data")
        layout = QVBoxLayout(self)

        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target dataset"))
        self.target_combo = QComboBox()

        for name in datasets:
            self.target_combo.addItem(name)

        self.target_combo.setCurrentText(current)
        self.processor = DataProcessor()
        
        self.use_selection = QCheckBox(
    "Use selection"
)

        self.use_selection.setChecked(
            use_selection
        )

        self.preserve_unselected = QCheckBox(
            "Preserve unselected data"
        )

        self.preserve_unselected.setChecked(True)

        self.preserve_unselected.setEnabled(
            self.use_selection.isChecked()
        )

        target_layout.addWidget(
            self.use_selection
        )

        target_layout.addWidget(
            self.preserve_unselected
        )
        layout.addLayout(target_layout)
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Column"))

        self.column_combo = QComboBox()

        controls.addWidget(self.column_combo)

        controls.addWidget(
            QLabel("Operation")
        )

        self.operation_button = QPushButton(
            "Select operation..."
        )

        self.operation_menu = QMenu(
            self.operation_button
        )

        self.build_operation_menu()

        self.operation_button.setMenu(
            self.operation_menu
        )

        controls.addWidget(
            self.operation_button
        )

        self.value_label = QLabel("Decimal places")
        self.decimal_places = QSpinBox()
        self.decimal_places.setRange(0, 12)
        self.decimal_places.setValue(2)
        self.type_combo = QComboBox()
        for dtype in DataType.TYPES:
            self.type_combo.addItem(
                dtype.title(),
                dtype
            )

        destination_layout = QHBoxLayout()

        destination_layout.addWidget(
            QLabel("Result")
        )
        self.replace_col_button = QRadioButton("Replace existing column")
        self.replace_col_button.setChecked(True)
        self.create_col_button = QRadioButton("Create new column")
        self.new_col_name = QLineEdit()
        self.new_col_name.setVisible(False)
        self.replace_col_button.toggled.connect(self.update_destination_controls)
        self.create_col_button.toggled.connect(self.update_destination_controls)
        self.new_col_name.textChanged.connect(
                self.update_preview
            )
        destination_layout.addWidget(
            self.replace_col_button
        )

        destination_layout.addWidget(
            self.create_col_button
        )

        destination_layout.addWidget(
            self.new_col_name
        )

        layout.addLayout(destination_layout)


        controls.addWidget(self.value_label)
        controls.addWidget(self.decimal_places)
        controls.addWidget(self.type_combo)
        layout.addLayout(controls)

        previews = QSplitter(Qt.Horizontal)
        previews.addWidget(self.preview)
        previews.addWidget(self.result_preview)
        layout.addWidget(previews)

        preview_labels = QHBoxLayout()
        preview_labels.addWidget(QLabel("Current data"))
        preview_labels.addWidget(QLabel("Transformed preview"))
        self.show_all_rows = QCheckBox("Show all rows")
        self.show_all_rows.toggled.connect(self.update_preview)
        preview_labels.addWidget(self.show_all_rows)
        layout.insertLayout(layout.indexOf(previews), preview_labels)

        buttons = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        self.apply_button = QPushButton("Apply")
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(self.apply_button)
        layout.addLayout(buttons)
        self.dataframe = self.get_dataframe()
        self.operation_dataframe = self.get_operation_dataframe()
        cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.apply)
        self.column_combo.currentIndexChanged.connect(self.update_operation_options)
        #self.operation_combo.currentIndexChanged.connect( self.on_operation_changed )
        self.decimal_places.valueChanged.connect(self.update_preview)
        self.type_combo.currentIndexChanged.connect(self.update_preview)
        self.target_combo.currentIndexChanged.connect(self.change_target)
        self.change_target()
        self.update_operation_options()
        self.use_selection.toggled.connect(self.change_target)
        self.use_selection.toggled.connect(
            self.update_selection_options
        )

        self.preserve_unselected.toggled.connect(
            self.update_preview
        )

    def get_dataset_key(self):
        return self.target_combo.currentText()


    def get_dataframe(self):

        info = self.datasets[
            self.get_dataset_key()
        ]

        return info["dataframe"].copy()

    def get_operation_dataframe(self):

        info = self.datasets[
            self.get_dataset_key()
        ]

        full_df = info["dataframe"].copy()

        if not self.use_selection.isChecked():
            return full_df

        return info["view"].get_analysis_dataframe().copy()


    def change_target(self):

        self.dataframe = self.get_dataframe()

        self.operation_dataframe = self.get_operation_dataframe()

        self.column_combo.clear()

        for column in self.operation_dataframe.columns:
            self.column_combo.addItem(
                str(column),
                column
            )

        self.update_operation_options()
        self.update_preview()

    def get_workspace(self):
        return self.datasets[self.get_dataset_key()]["workspace"]


    def get_target(self):
        return self.datasets[self.get_dataset_key()]["target"]

    def update_operation_options(self):
        """Rebuild the menu for the selected column."""

        column = self.column_combo.currentData()

        if column is None:
            self.operation_button.setEnabled(False)
            return

        self.operation_button.setEnabled(True)

        series = self.operation_dataframe[column]

        numeric = (
            pd.api.types.is_numeric_dtype(series)
            and not pd.api.types.is_bool_dtype(series)
        )

        text = (
            pd.api.types.is_string_dtype(series)
            or pd.api.types.is_object_dtype(series)
            or pd.api.types.is_categorical_dtype(series)
        )

        datetime = pd.api.types.is_datetime64_any_dtype(series)

        # <-- THIS IS THE IMPORTANT LINE
        self.build_operation_menu(
            numeric=numeric,
            text=text,
            datetime=datetime,
        )

        # Reset invalid selection
        if self.operation not in self.operation_actions:
            self.operation = None
            self.operation_button.setText("Select operation...")

        self.update_value_controls()
        self.update_preview()

    def update_value_controls(self):

        operation = self.operation

        is_round = operation == "round"
        is_astype = operation == "astype"

        self.decimal_places.setVisible(is_round)
        self.type_combo.setVisible(is_astype)

        if is_round:
            self.value_label.setText("Decimal places")

        elif is_astype:
            self.value_label.setText("Target type")

        else:
            self.value_label.clear()

    def get_transform(self):

        operation = self.operation

        value = None

        if operation == "round":
            value = self.decimal_places.value()

        elif operation == "astype":
            value = self.type_combo.currentData()

        destination = (
            "new"
            if self.create_col_button.isChecked()
            else "replace"
        )

        new_column = None

        if destination == "new":
            new_column = self.new_col_name.text().strip()

        return TransformConfig(
            column=self.column_combo.currentData(),
            operation=operation,
            value=value,
            destination=destination,
            new_column=new_column
        )

    def update_preview(self):

        full = self.show_all_rows.isChecked()

        self.preview.display_dataframe(
            self.operation_dataframe,
            full=full
        )
        if self.operation is None:

            self.result_preview.clearContents()
            self.result_preview.setRowCount(0)

            self.apply_button.setEnabled(False)

            return
        
        try:

            config = self.get_transform()

            operation_result = self.processor.transform(
                self.operation_dataframe,
                config
            )

            if (
                self.use_selection.isChecked()
                and self.preserve_unselected.isChecked()
            ):

                result = self.merge_selection_result(
                self.dataframe,
                operation_result
            )

            else:

                result = operation_result

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            self.result_preview.clearContents()
            self.result_preview.setRowCount(0)
            self.apply_button.setEnabled(False)

            return

        self.result_preview.display_dataframe(
            result,
            full=full
        )

        self.result = result
        self.apply_button.setEnabled(True)


    def update_selection_options(self, checked):

        self.preserve_unselected.setEnabled(
            checked
        )

        self.change_target()

    def merge_selection_result(
        self,
        original,
        result
    ):

        merged = original.copy()

        for column in result.columns:

            if column not in merged.columns:
                merged[column] = pd.NA

            common = result.index.intersection(
                merged.index
            )

            merged.loc[
                common,
                column
            ] = result.loc[
                common,
                column
            ]

        return merged

    def apply(self):

        try:

            config = self.get_transform()

            operation_result = self.processor.transform(
                self.operation_dataframe,
                config
            )

            if (
                self.use_selection.isChecked()
                and self.preserve_unselected.isChecked()
            ):

                result = self.merge_selection_result(
                    self.dataframe,
                    operation_result
                )

            else:

                result = operation_result

            self.result = result
            self.accept()

        except (
            KeyError,
            TypeError,
            ValueError
        ) as error:

            QMessageBox.warning(
                self,
                "Transform Failed",
                str(error)
            )

    def get_result(self):
        return self.result



    def update_destination_controls(self):

        is_new = self.create_col_button.isChecked()

        self.new_col_name.setVisible(is_new)

        if is_new:

            self.new_col_name.setText(
                self.default_new_column_name()
            )

        self.update_preview()

    def default_new_column_name(self):

        column = self.column_combo.currentData()
        operation = self.operation

        if column is None or operation is None:
            return ""

        suffixes = {
            "normalize": "normalized",
            "absolute": "absolute",
            "round": "rounded",
            "standardize": "standardized",
            "rank": "rank",
            "uppercase": "uppercase",
            "lowercase": "lowercase",
            "title_case": "title",
            "trim": "trimmed",
            "remove_whitespace": "no_whitespace",
            "capitalize_first": "capitalized",
            "length": "length",
            "extract_year": "year",
            "extract_month": "month",
            "extract_day": "day",
            "extract_weekday": "weekday",
            "extract_weekend": "weekend",
            "extract_time": "time",
            "extract_quarter": "quarter",
            "extract_month_name": "month_name",
            "extract_day_name": "day_name",
            "extract_hour": "hour",
            "extract_minute": "minute",
            "astype": self.type_combo.currentData(),
        }

        suffix = suffixes.get(operation, operation)

        return f"{column}_{suffix}"


    def build_operation_menu(self, numeric=False, text=False, datetime=False):

        self.operation_menu.clear()
        self.operation_actions = {}

        if numeric:
            menu = self.operation_menu.addMenu("Numeric")

            self.add_operation(menu, "Round", "round")
            self.add_operation(menu, "Absolute value", "absolute")
            self.add_operation(menu, "Normalize", "normalize")
            self.add_operation(menu, "Standardize", "standardize")
            self.add_operation(menu, "Rank", "rank")

        if text:
            menu = self.operation_menu.addMenu("Text")

            self.add_operation(menu, "Uppercase", "uppercase")
            self.add_operation(menu, "Lowercase", "lowercase")
            self.add_operation(menu, "Title case", "title_case")
            self.add_operation(menu, "Trim", "trim")
            self.add_operation(menu, "Remove whitespace", "remove_whitespace")
            self.add_operation(menu, "Capitalize first", "capitalize_first")
            self.add_operation(menu, "Length", "length")

        if datetime:
            menu = self.operation_menu.addMenu("Date / Time")

            self.add_operation(menu, "Extract year", "extract_year")
            self.add_operation(menu, "Extract month", "extract_month")
            self.add_operation(menu, "Extract weekday", "extract_weekday")
            self.add_operation(menu, "Extract hour", "extract_hour")

        # Always available
        type_menu = self.operation_menu.addMenu("Type")
        self.add_operation(type_menu, "Change type", "astype")

    def add_operation(self, menu, label, value):
        """Add an operation action to a menu."""

        action = menu.addAction(label)

        action.setData(value)

        action.triggered.connect(
            lambda checked=False, action=action:
            self.select_operation(action)
        )

        self.operation_actions[value] = action

    def select_operation(self, action):
        """Set the currently selected operation."""

        value = action.data()

        self.operation = value

        self.operation_button.setText(
            action.text()
        )

        self.update_value_controls()
        self.update_preview()