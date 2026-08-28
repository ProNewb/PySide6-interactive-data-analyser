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
    QVBoxLayout
)

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

        controls.addWidget(QLabel("Operation"))
        self.operation_combo = QComboBox()

        self.add_operation_category("Numeric")

        for label, value in (
            ("Round", "round"),
            ("Absolute value", "absolute"),
            ("Normalize", "normalize"),
            ("Standardize", "standardize"),
            ("Rank", "rank"),
        ):
            self.operation_combo.addItem(label, value)

        self.operation_combo.insertSeparator(
            self.operation_combo.count()
        )

        self.add_operation_category("Text")

        for label, value in (
            ("Uppercase", "uppercase"),
            ("Lowercase", "lowercase"),
            ("Title case", "title_case"),
            ("Trim", "trim"),
            ("Remove whitespace", "remove_whitespace"),
            ("Capitalize first letter", "capitalize_first"),
            ("Length" , "length")
        ):
            self.operation_combo.addItem(label, value)

        self.operation_combo.insertSeparator(
            self.operation_combo.count()
        )

        self.add_operation_category("Type")

        self.operation_combo.addItem(
            "Change type",
            "astype"
        )

        self.operation_combo.insertSeparator(
            self.operation_combo.count()
        )

        self.add_operation_category("Date / Time")

        for label, value in (
            ("Extract year", "extract_year"),
            ("Extract month", "extract_month"),
            ("Extract day", "extract_day"),
            ("Extract weekday", "extract_weekday"),
            ("Extract weekend", "extract_weekend"),
            ("Extract time", "extract_time"),
            ("Extract quarter", "extract_quarter"),
            ("Extract month name", "extract_month_name"),
            ("Extract day name", "extract_day_name"),
            ("Extract hour", "extract_hour"),
            ("Extract minute", "extract_minute"),

        ):
            self.operation_combo.addItem(label, value)
        controls.addWidget(self.operation_combo)

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
        self.operation_combo.currentIndexChanged.connect(self.update_preview)
        self.operation_combo.currentIndexChanged.connect(
            self.update_value_controls
        )
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

        column = self.column_combo.currentData()

        if column is None:
            self.apply_button.setEnabled(False)
            return

        series = self.operation_dataframe[column]

        numeric = (
            pd.api.types.is_numeric_dtype(series)
            and not pd.api.types.is_bool_dtype(series)
        )

        text = (
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_string_dtype(series)
            or pd.api.types.is_categorical_dtype(series)
        )

        datetime = (
            pd.api.types.is_datetime64_any_dtype(series)
        )

        allowed = {
            "round": numeric,
            "absolute": numeric,
            "normalize": numeric,
            "standardize": numeric,
            "rank": numeric,
            "uppercase": text,
            "lowercase": text,
            "title_case": text,
            "trim": text,
            "remove_whitespace": text,
            "capitalize_first": text,
            "length": text,
            "astype": True,

            "extract_year": datetime,
            "extract_month": datetime,
            "extract_day": datetime,
            "extract_weekday": datetime,
            "extract_weekend": datetime,
            "extract_time": datetime,
            "extract_quarter": datetime,
            "extract_month_name": datetime,
            "extract_day_name": datetime,
            "extract_hour": datetime,
            "extract_minute": datetime,
        }

        for index in range(self.operation_combo.count()):

            operation = self.operation_combo.itemData(index)

            # Category labels / separators
            if operation is None:
                continue

            item = self.operation_combo.model().item(index)

            item.setEnabled(
                allowed.get(operation, False)
            )

        current_operation = (
            self.operation_combo.currentData()
        )

        if (
            current_operation is not None
            and not allowed.get(current_operation, False)
        ):
            self.operation_combo.setCurrentIndex(
                self.operation_combo.findData("astype")
            )

        self.update_value_controls()
        self.update_preview()

    def update_value_controls(self):

        operation = self.operation_combo.currentData()

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

        operation = self.operation_combo.currentData()

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

    def add_operation_category(self, text):

        self.operation_combo.addItem(text)

        index = self.operation_combo.count() - 1

        item = self.operation_combo.model().item(index)

        item.setEnabled(False)

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
        operation = self.operation_combo.currentData()

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