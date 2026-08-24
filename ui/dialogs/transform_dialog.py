from PySide6.QtCore import Qt
import pandas as pd
from PySide6.QtWidgets import (
    QComboBox,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout
)

from core.data_processor import TransformConfig
from ui.table.preview_table import PreviewTable


class TransformDialog(QDialog):
    """Configure a column transform and preview its result."""

    def __init__(self, dataframe, parent=None, target_dataframes=None,
                 target="main"):
        super().__init__(parent)
        self.dataframe = dataframe
        self.target_dataframes = target_dataframes or {target: dataframe}
        self.preview = PreviewTable()
        self.result_preview = PreviewTable()

        self.setWindowTitle("Transform Data")
        layout = QVBoxLayout(self)

        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target dataset"))
        self.target_combo = QComboBox()
        for key, label in (("main", "Main Dataset"),
                           ("result", "Result Dataset")):
            if key in self.target_dataframes:
                self.target_combo.addItem(label, key)
        self.target_combo.setCurrentIndex(
            max(0, self.target_combo.findData(target))
        )
        target_layout.addWidget(self.target_combo)
        layout.addLayout(target_layout)
        self.use_selection = QCheckBox("Use selection")


        layout.addWidget(
            self.use_selection
        )
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Column"))
        self.column_combo = QComboBox()
        for column in dataframe.columns:
            self.column_combo.addItem(str(column), column)
        controls.addWidget(self.column_combo)

        controls.addWidget(QLabel("Operation"))
        self.operation_combo = QComboBox()
        for label, value in (
            ("Round", "round"),
            ("Uppercase", "uppercase"),
            ("Lowercase", "lowercase"),
            ("Trim", "trim"),
            ("Remove whitespace", "remove_whitespace"),
            ("Capitalize first letter", "capitalize_first"),
            ("Change type", "astype")
        ):
            self.operation_combo.addItem(label, value)
        controls.addWidget(self.operation_combo)

        self.value_label = QLabel("Decimal places")
        self.decimal_places = QSpinBox()
        self.decimal_places.setRange(0, 12)
        self.decimal_places.setValue(2)
        self.type_combo = QComboBox()
        for label, dtype in (
            ("Integer", "Int64"),
            ("Decimal", "Float64"),
            ("Text", "string"),
            ("Boolean", "boolean"),
            ("Date/time", "datetime64[ns]")
        ):
            self.type_combo.addItem(label, dtype)
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

        cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.accept)
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

    def get_target(self):
        return self.target_combo.currentData()

    def change_target(self):
        if not hasattr(self, "column_combo"):
            return
        self.dataframe = self.target_dataframes[self.get_target()]
        self.column_combo.clear()
        for column in self.dataframe.columns:
            self.column_combo.addItem(str(column), column)
        self.update_operation_options()

    def update_operation_options(self):
        column = self.column_combo.currentData()
        if column is None:
            self.apply_button.setEnabled(False)
            return

        series = self.dataframe[column]
        numeric = (
            pd.api.types.is_numeric_dtype(series)
            and not pd.api.types.is_bool_dtype(series)
        )
        text = (
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_string_dtype(series)
        )
        allowed = {
            "round": numeric,
            "uppercase": text,
            "lowercase": text,
            "trim": text,
            "remove_whitespace": text,
            "capitalize_first": text,
            "astype": True
        }

        for index in range(self.operation_combo.count()):
            operation = self.operation_combo.itemData(index)
            self.operation_combo.model().item(index).setEnabled(
                allowed[operation]
            )

        if not allowed[self.operation_combo.currentData()]:
            self.operation_combo.setCurrentIndex(
                self.operation_combo.findData("astype")
            )
        self.update_value_controls()
        self.update_preview()

    def update_value_controls(self):
        is_round = self.operation_combo.currentData() == "round"
        is_astype = self.operation_combo.currentData() == "astype"
        self.value_label.setText(
            "Decimal places" if is_round else "Target type"
        )
        self.decimal_places.setVisible(is_round)
        self.type_combo.setVisible(is_astype)

    def get_transform(self):
        operation = self.operation_combo.currentData()
        value = self.type_combo.currentData()
        if operation == "round":
            value = self.decimal_places.value()
        return TransformConfig(
            self.column_combo.currentData(),
            operation,
            value
        )

    def update_preview(self):
        full = self.show_all_rows.isChecked()
        self.preview.display_dataframe(self.dataframe, full=full)
        try:
            config = self.get_transform()
            result = self.dataframe.copy()
            column = config.column
            if config.operation == "round":
                result[column] = result[column].round(config.value)
            elif config.operation == "uppercase":
                result[column] = result[column].str.upper()
            elif config.operation == "lowercase":
                result[column] = result[column].str.lower()
            elif config.operation == "trim":
                result[column] = result[column].str.strip()
            elif config.operation == "remove_whitespace":
                result[column] = result[column].str.replace(
                    r"\s+", "", regex=True
                )
            elif config.operation == "capitalize_first":
                result[column] = result[column].str.replace(
                    r"^(\s*)(\S)",
                    lambda match: (
                        match.group(1) + match.group(2).upper()
                    ),
                    regex=True
                )
            elif config.operation == "astype":
                result[column] = result[column].astype(config.value)
        except (KeyError, TypeError, ValueError):
            self.result_preview.clearContents()
            self.result_preview.setRowCount(0)
            self.apply_button.setEnabled(False)
            return

        self.result_preview.display_dataframe(result, full=full)
        self.apply_button.setEnabled(True)
