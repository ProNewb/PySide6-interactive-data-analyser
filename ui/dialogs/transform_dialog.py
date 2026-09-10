from PySide6.QtCore import Qt
import pandas as pd
import numpy as np
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
    QDoubleSpinBox,
    QSplitter,
    QVBoxLayout,
    QMenu,
    QStackedWidget,
    QWidget,
)

from core.data_processor import (
    DataProcessor,
    DataType,
    TransformConfig,
    MultiColumnTransformConfig,
    CalculationConfig,
    CalculationOperand,
)
from PySide6.QtGui import QAction

from ui.table.preview_table import PreviewTable


class TransformDialog(QDialog):
    """Configure single-column, multi-column and calculated transforms."""

    def __init__(
        self,
        datasets,
        parent=None,
        current=None,
        use_selection=False,
    ):
        super().__init__(parent)

        self.datasets = datasets
        self.processor = DataProcessor()

        self.operation = None
        self.result = None
        
        self.column_rows = []

        self.setWindowTitle("Transform Data")
        self.resize(1000, 700)

        layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # Target
        # ---------------------------------------------------------

        target_layout = QHBoxLayout()

        target_layout.addWidget(
            QLabel("Target dataset")
        )

        self.target_combo = QComboBox()

        for name in datasets:
            self.target_combo.addItem(name)

        if current in datasets:
            self.target_combo.setCurrentText(current)

        target_layout.addWidget(
            self.target_combo
        )

        self.use_selection = QCheckBox(
            "Use selection"
        )
        self.use_selection.setChecked(
            use_selection
        )

        target_layout.addWidget(
            self.use_selection
        )

        self.preserve_unselected = QCheckBox(
            "Preserve unselected data"
        )
        self.preserve_unselected.setChecked(True)
        self.preserve_unselected.setEnabled(
            use_selection
        )

        target_layout.addWidget(
            self.preserve_unselected
        )

        layout.addLayout(target_layout)

        # ---------------------------------------------------------
        # Source columns
        # ---------------------------------------------------------

        source_header = QHBoxLayout()

        self.source_label = QLabel(
            "Source columns"
        )

        source_header.addWidget(
            self.source_label
        )

        self.add_column_button = QPushButton("+ Add column")
        self.add_column_button.clicked.connect(
            self.add_column_row
        )

        source_header.addWidget(
            self.add_column_button
        )

        source_header.addStretch()

        layout.addLayout(source_header)

        self.columns_layout = QVBoxLayout()
        layout.addLayout(self.columns_layout)

        

        # ---------------------------------------------------------
        # Operation
        # ---------------------------------------------------------

        operation_layout = QHBoxLayout()

        operation_layout.addWidget(
            QLabel("Operation")
        )

        self.operation_button = QPushButton(
            "Select operation..."
        )

        self.operation_menu = QMenu(
            self.operation_button
        )

        self.operation_button.setMenu(
            self.operation_menu
        )

        operation_layout.addWidget(
            self.operation_button
        )

        operation_layout.addStretch()

        layout.addLayout(operation_layout)

        # ---------------------------------------------------------
        # Value/input controls
        # ---------------------------------------------------------

        self.value_widget = QWidget()

        self.value_layout = QHBoxLayout(
            self.value_widget
        )

        self.value_layout.setContentsMargins(
            0, 0, 0, 0
        )

        self.value_label = QLabel()

        self.value_layout.addWidget(
            self.value_label
        )

        self.decimal_places = QSpinBox()
        self.decimal_places.setRange(0, 12)
        self.decimal_places.setValue(2)

        self.type_combo = QComboBox()

        for dtype in DataType.TYPES:
            self.type_combo.addItem(
                dtype.title(),
                dtype
            )

        self.value_edit = QLineEdit()

        self.find_edit = QLineEdit()

        self.replace_edit = QLineEdit()

        self.pattern_edit = QLineEdit()

        self.clip_min = QDoubleSpinBox()
        self.clip_min.setRange(
            -1_000_000_000,
            1_000_000_000
        )
        self.clip_min.setDecimals(6)

        self.clip_max = QDoubleSpinBox()
        self.clip_max.setRange(
            -1_000_000_000,
            1_000_000_000
        )
        self.clip_max.setDecimals(6)
        self.clip_max.setValue(100)

        self.substring_start = QSpinBox()
        self.substring_start.setRange(
            0,
            1_000_000
        )

        self.substring_end = QSpinBox()
        self.substring_end.setRange(
            0,
            1_000_000
        )
        self.substring_end.setValue(10)

        self.pad_width = QSpinBox()
        self.pad_width.setRange(
            1,
            1000
        )
        self.pad_width.setValue(10)

        self.separator_edit = QLineEdit()
        self.separator_edit.setText(" ")

        # ---------------------------------------------------------
        # Add all controls to the layout
        # ---------------------------------------------------------

        for widget in (
            self.decimal_places,
            self.type_combo,
            self.value_edit,
            self.find_edit,
            self.replace_edit,
            self.pattern_edit,
            self.clip_min,
            self.clip_max,
            self.substring_start,
            self.substring_end,
            self.pad_width,
            self.separator_edit,
        ):
            self.value_layout.addWidget(widget)

        # ---------------------------------------------------------
        # Signals
        # ---------------------------------------------------------

        for widget in (
            self.decimal_places,
            self.clip_min,
            self.clip_max,
            self.substring_start,
            self.substring_end,
            self.pad_width,
        ):
            widget.valueChanged.connect(
                self.update_preview
            )

        for widget in (
            self.type_combo,
            self.value_edit,
            self.find_edit,
            self.replace_edit,
            self.pattern_edit,
            self.separator_edit,
        ):
            if isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(
                    self.update_preview
                )
            else:
                widget.textChanged.connect(
                    self.update_preview
                )

        layout.addWidget(
            self.value_widget
        )

        # ---------------------------------------------------------
        # Destination
        # ---------------------------------------------------------

        self.destination_widget = QWidget()

        destination_layout = QHBoxLayout(
            self.destination_widget
        )

        destination_layout.setContentsMargins(
            0, 0, 0, 0
        )

        destination_layout.addWidget(
            QLabel("Result")
        )

        self.replace_col_button = QRadioButton(
            "Replace existing column"
        )
        self.replace_col_button.setChecked(True)

        self.create_col_button = QRadioButton(
            "Create new column"
        )

        self.new_col_name = QLineEdit()
        self.new_col_name.setPlaceholderText(
            "New column name"
        )

        self.new_col_name.setVisible(False)

        destination_layout.addWidget(
            self.replace_col_button
        )

        destination_layout.addWidget(
            self.create_col_button
        )

        destination_layout.addWidget(
            self.new_col_name
        )

        destination_layout.addStretch()

        layout.addWidget(
            self.destination_widget
        )

        # ---------------------------------------------------------
        # Preview
        # ---------------------------------------------------------

        previews = QSplitter(Qt.Horizontal)

        self.preview = PreviewTable()
        self.result_preview = PreviewTable()

        previews.addWidget(
            self.preview
        )
        previews.addWidget(
            self.result_preview
        )

        layout.addWidget(
            previews
        )

        preview_labels = QHBoxLayout()

        preview_labels.addWidget(
            QLabel("Current data")
        )

        preview_labels.addWidget(
            QLabel("Transformed preview")
        )

        self.show_all_rows = QCheckBox(
            "Show all rows"
        )

        self.show_all_rows.toggled.connect(
            self.update_preview
        )

        preview_labels.addWidget(
            self.show_all_rows
        )

        layout.insertLayout(
            layout.indexOf(previews),
            preview_labels
        )

        # ---------------------------------------------------------
        # Buttons
        # ---------------------------------------------------------

        buttons = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        self.apply_button = QPushButton("Apply")

        buttons.addStretch()

        buttons.addWidget(
            cancel_button
        )

        buttons.addWidget(
            self.apply_button
        )

        layout.addLayout(buttons)

        # ---------------------------------------------------------
        # Signals
        # ---------------------------------------------------------

        cancel_button.clicked.connect(
            self.reject
        )

        self.apply_button.clicked.connect(
            self.apply
        )

        self.target_combo.currentIndexChanged.connect(
            self.change_target
        )

        self.use_selection.toggled.connect(
            self.change_selection_mode
        )

        self.preserve_unselected.toggled.connect(
            self.update_preview
        )

        self.replace_col_button.toggled.connect(
            self.update_destination_controls
        )

        self.create_col_button.toggled.connect(
            self.update_destination_controls
        )

        self.new_col_name.textChanged.connect(
            self.update_preview
        )


        # ---------------------------------------------------------
        # Initial data
        # ---------------------------------------------------------
        
        self.dataframe = pd.DataFrame()
        self.operation_dataframe = pd.DataFrame()

        # Now target_combo exists, so this is safe.
        self.dataframe = self.get_dataframe()
        self.operation_dataframe = self.get_operation_dataframe()

        # Now column rows can safely access operation_dataframe.
        self.add_column_row()

        #self.refresh_column_rows()
        self.update_operation_options()
        self.update_destination_controls()
        self.update_preview()

    # =============================================================
    # DATASET
    # =============================================================

    def get_dataset_key(self):
        return self.target_combo.currentText()

    def get_dataset_info(self):
        return self.datasets[
            self.get_dataset_key()
        ]

    def get_dataframe(self):
        return self.get_dataset_info()[
            "dataframe"
        ].copy()

    def get_operation_dataframe(self):
        info = self.get_dataset_info()

        full_df = info[
            "dataframe"
        ].copy()

        if not self.use_selection.isChecked():
            return full_df

        return info[
            "view"
        ].get_analysis_dataframe().copy()

    def get_workspace(self):
        return self.get_dataset_info()[
            "workspace"
        ]

    def get_target(self):
        return self.get_dataset_info()[
            "target"
        ]

    def change_target(self):
        self.dataframe = self.get_dataframe()
        self.operation_dataframe = (
            self.get_operation_dataframe()
        )

        self.refresh_column_rows()
        self.update_operation_options()
        self.update_preview()

    def change_selection_mode(self):
        checked = self.use_selection.isChecked()

        self.preserve_unselected.setEnabled(
            checked
        )

        self.change_target()

    # =============================================================
    # SOURCE COLUMN ROWS
    # =============================================================

    def add_column_row(self):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)

        row_layout.setContentsMargins(
            0, 0, 0, 0
        )

        combo = QComboBox()

        constant_edit = QLineEdit()
        constant_edit.setPlaceholderText(
            "Constant"
        )
        constant_edit.setVisible(False)

        operator_combo = QComboBox()

        for operator in DataType.OPERATORS:
            operator_combo.addItem(
                operator,
                operator
            )

        remove_button = QPushButton("×")
        remove_button.setFixedWidth(30)

        row_layout.addWidget(combo)
        row_layout.addWidget(constant_edit)
        row_layout.addWidget(operator_combo)
        row_layout.addWidget(remove_button)

        self.columns_layout.addWidget(
            row_widget
        )

        self.column_rows.append(
            (
                row_widget,
                combo,
                constant_edit,
                operator_combo,
                remove_button,
            )
        )

        combo.currentIndexChanged.connect(
            self.source_columns_changed
        )

        constant_edit.textChanged.connect(
            self.source_columns_changed
        )

        operator_combo.currentIndexChanged.connect(
            self.update_preview
        )

        remove_button.clicked.connect(
            lambda: self.remove_column_row(
                row_widget
            )
        )

        self.populate_column_combo(combo)

        self.update_column_row_buttons()
        self.update_operator_rows()
        self.update_operation_options()


    def remove_column_row(self, widget):
        if len(self.column_rows) <= 1:
            return

        for index, item in enumerate(
            self.column_rows
        ):
            row_widget, _, _, _, _ = item

            if row_widget is widget:
                self.columns_layout.removeWidget(
                    row_widget
                )

                row_widget.deleteLater()

                self.column_rows.pop(index)
                break

        self.update_column_row_buttons()
        self.update_operator_rows()
        self.update_operation_options()
        self.update_preview()

    def update_column_row_buttons(self):
        show_remove = (
            len(self.column_rows) > 1
        )

        for (
            row_widget,
            combo,
            constant_edit,
            operator_combo,
            remove_button,
        ) in self.column_rows:

            remove_button.setVisible(
                show_remove
            )

    def populate_column_combo(self, combo, preferred=None):
        current = combo.currentData()

        combo.blockSignals(True)
        combo.clear()

        for column in self.operation_dataframe.columns:
            combo.addItem(
                str(column),
                ("column", column)
            )

        combo.addItem(
            "Constant",
            ("constant", None)
        )

        # Prefer a supplied value.
        if preferred is not None:
            for index in range(combo.count()):
                if combo.itemData(index) == (
                    "column",
                    preferred
                ):
                    combo.setCurrentIndex(index)
                    break

        # Otherwise restore previous selection.
        elif current is not None:
            for index in range(combo.count()):
                if combo.itemData(index) == current:
                    combo.setCurrentIndex(index)
                    break

        combo.blockSignals(False)

    def source_columns_changed(self):
        self.update_operation_options()
        self.update_column_rows_for_operation()
        self.update_destination_controls()
        self.update_preview()

    # =============================================================
    # OPERATION MENU
    # =============================================================

    def update_operation_options(self):
        columns = self.get_selected_columns()

        self.build_operation_menu(
            columns
        )

    def get_dtype_group(self, series):
        if pd.api.types.is_bool_dtype(series):
            return "boolean"

        if pd.api.types.is_numeric_dtype(series):
            return "numeric"

        if pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"

        if pd.api.types.is_categorical_dtype(series):
            return "category"

        if pd.api.types.is_string_dtype(series):
            return "text"

        return "other"

    def refresh_column_rows(self):
        for (
            _,
            combo,
            _,
            _,
            _,
        ) in self.column_rows:

            self.populate_column_combo(
                combo
            )

    def operation_allowed(
        self,
        operation,
        columns,
    ):
        spec = DataType.TRANSFORM_OPERATIONS.get(
            operation
        )

        if spec is None:
            return False

        count = len(columns)

        minimum = spec.get(
            "min_columns",
            1
        )

        maximum = spec.get(
            "max_columns"
        )

        if count < minimum:
            return False

        if (
            maximum is not None
            and count > maximum
        ):
            return False

        # Multi-column transforms require distinct columns.
        if (
            spec.get("mode") == "multi"
            and len(columns) != len(set(columns))
        ):
            return False

        allowed = (
            spec.get("allowed_dtypes")
            or spec.get("dtype")
        )

        if allowed is None:
            return True

        if isinstance(
            allowed,
            str
        ):
            allowed = {
                allowed
            }

        groups = {
            self.get_dtype_group(
                self.operation_dataframe[column]
            )
            for column in columns
        }

        if "any" in allowed:
            return True

        return groups.issubset(
            set(allowed)
        )

    def build_operation_menu(self, columns=None):
        if columns is None:
            columns = []

        self.operation_menu.clear()
        self.operation_actions = {}

        self.operation_button.setEnabled(
            bool(columns)
        )

        grouped = {}

        for operation, spec in (
            DataType.TRANSFORM_OPERATIONS.items()
        ):
            if not self.operation_allowed(
                operation,
                columns
            ):
                continue

            group = spec.get(
                "group",
                "Other"
            )

            grouped.setdefault(
                group,
                []
            ).append(
                operation
            )

        # Calculation is a separate mode.
        if len(columns) >= 1:
            grouped.setdefault(
                "Calculate",
                []
            ).append(
                "__calculate__"
            )

        for group, operations in grouped.items():
            menu = self.operation_menu.addMenu(
                group
            )

            for operation in operations:

                if operation == "__calculate__":
                    action = menu.addAction(
                        "Calculated expression"
                    )

                    action.setData(
                        operation
                    )

                    action.triggered.connect(
                        lambda checked=False,
                        action=action:
                        self.select_operation(
                            action
                        )
                    )

                    self.operation_actions[
                        operation
                    ] = action

                    continue

                spec = DataType.TRANSFORM_OPERATIONS[
                    operation
                ]

                label = spec.get(
                    "label",
                    operation.replace(
                        "_",
                        " "
                    ).title()
                )

                self.add_operation(
                    menu,
                    label,
                    operation
                )

        if not self.operation_actions:
            self.operation = None

            self.operation_button.setText(
                "No valid operations"
            )

            self.update_value_controls()
            self.update_destination_controls()
            self.update_column_rows_for_operation()

            return

        if self.operation not in self.operation_actions:
            self.operation = None

            self.operation_button.setText(
                "Select operation..."
            )

        self.update_value_controls()
        self.update_destination_controls()
        self.update_column_rows_for_operation()

    def add_operation(
        self,
        menu,
        label,
        value,
    ):
        action = menu.addAction(
            label
        )

        action.setData(
            value
        )

        action.triggered.connect(
            lambda checked=False,
            action=action:
            self.select_operation(
                action
            )
        )

        self.operation_actions[
            value
        ] = action

    def select_operation(self, action):
        self.operation = action.data()

        self.operation_button.setText(
            action.text()
        )

        self.update_column_rows_for_operation()
        self.update_value_controls()
        self.update_destination_controls()
        self.update_preview()

    # =============================================================
    # VALUE CONTROLS
    # =============================================================

    def clear_value_controls(self):
        while self.value_layout.count():
            item = self.value_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()


    def update_value_controls(self):
        operation = self.operation

        # Hide everything first
        self.decimal_places.setVisible(False)
        self.type_combo.setVisible(False)

        self.value_edit.setVisible(False)

        self.find_edit.setVisible(False)
        self.replace_edit.setVisible(False)

        self.pattern_edit.setVisible(False)

        self.clip_min.setVisible(False)
        self.clip_max.setVisible(False)

        self.substring_start.setVisible(False)
        self.substring_end.setVisible(False)

        self.pad_width.setVisible(False)
        self.separator_edit.setVisible(False)

        if operation is None:
            return

        # -------------------------
        # Type conversion
        # -------------------------
        if operation == "astype":
            self.type_combo.setVisible(True)
            return

        # -------------------------
        # Numeric value
        # -------------------------
        if operation in {
            "power",
            "modulus",
            "contains",
            "startswith",
            "endswith",
            "count_occurrences",
            
        }:
            self.value_edit.setVisible(True)
            return

        # -------------------------
        # Clip
        # -------------------------
        if operation == "clip":
            self.clip_min.setVisible(True)
            self.clip_max.setVisible(True)
            return


        # -------------------------
        # Find / replace
        # -------------------------
        if operation in {
            "find_and_replace",
            "replace",
        }:
            self.find_edit.setVisible(True)
            self.replace_edit.setVisible(True)
            return

        # -------------------------
        # Replace entire cell
        # -------------------------
        if operation == "replace_all":
            self.replace_edit.setVisible(True)
            return

        # -------------------------
        # Regex replacement
        # -------------------------
        if operation in {
            "regex_replace",
            "regex_replace_all",
        }:
            self.pattern_edit.setVisible(True)
            self.replace_edit.setVisible(True)
            return

        # -------------------------
        # Regex matching/extraction
        # -------------------------
        if operation in {
            "regex_extract",
            "regex_match",
            "regex_findall",
        }:
            self.pattern_edit.setVisible(True)
            return

        # -------------------------
        # Substring
        # -------------------------
        if operation in {
            "substring",
            "extract_substring",
        }:
            self.substring_start.setVisible(True)
            self.substring_end.setVisible(True)
            return

        # -------------------------
        # Padding
        # -------------------------
        if operation == "pad":
            self.pad_width.setVisible(True)
            return

        # -------------------------
        # Concatenation
        # -------------------------
        if operation == "concatenate":
            self.separator_edit.setVisible(True)
            return

        # -------------------------
        # Decimal places
        # -------------------------
        if operation in {
            "round",
            "round_to",
        }:
            self.decimal_places.setVisible(True)

    # =============================================================
    # DESTINATION
    # =============================================================

    def update_destination_controls(self):
        operation = self.operation

        if operation is None:
            self.destination_widget.setVisible(False)
            return

        # --------------------------------------------------
        # Calculated expression
        # --------------------------------------------------

        if operation == "__calculate__":
            self.destination_widget.setVisible(True)

            self.replace_col_button.setVisible(False)
            self.create_col_button.setVisible(False)

            self.new_col_name.setVisible(True)

            if not self.new_col_name.text().strip():
                self.new_col_name.setText("calculated")

            return

        spec = DataType.TRANSFORM_OPERATIONS.get(
            operation,
            {}
        )

        mode = spec.get("mode", "single")

        # --------------------------------------------------
        # Forced-new operations
        # --------------------------------------------------

        if (
            spec.get("destination") == "new"
            or mode == "multi"
        ):
            self.destination_widget.setVisible(True)

            self.replace_col_button.setVisible(False)
            self.create_col_button.setVisible(False)

            self.new_col_name.setVisible(True)

            if not self.new_col_name.text().strip():
                self.new_col_name.setText(
                    self.default_new_column_name()
                )

            return

        # --------------------------------------------------
        # Normal single-column operation
        # --------------------------------------------------

        self.destination_widget.setVisible(True)

        self.replace_col_button.setVisible(True)
        self.create_col_button.setVisible(True)

        self.new_col_name.setVisible(
            self.create_col_button.isChecked()
        )
    # =============================================================
    # CALCULATIONS
    # =============================================================
    def get_selected_columns(self):
        columns = []

        for (
            _,
            combo,
            _,
            _,
            _,
        ) in self.column_rows:

            data = combo.currentData()

            if not data:
                continue

            operand_type, value = data

            if operand_type == "column":
                columns.append(value)

        return columns





    def get_calculation(self):
        name = self.new_col_name.text().strip()

        if not name:
            raise ValueError(
                "A calculated column name is required."
            )

        operands = []
        operators = []

        for index, (
            row_widget,
            combo,
            constant_edit,
            operator_combo,
            remove_button,
        ) in enumerate(self.column_rows):

            data = combo.currentData()

            if not data:
                continue

            operand_type, value = data

            if operand_type == "column":
                operands.append(
                    CalculationOperand(
                        type="column",
                        value=value,
                    )
                )

            elif operand_type == "constant":
                text = constant_edit.text().strip()

                if not text:
                    raise ValueError(
                        "Enter a value for every constant."
                    )

                try:
                    constant = float(text)
                except ValueError:
                    raise ValueError(
                        f"Invalid constant: {text}"
                    )

                operands.append(
                    CalculationOperand(
                        type="constant",
                        value=constant,
                    )
                )

            if index < len(self.column_rows) - 1:
                operators.append(
                    operator_combo.currentData()
                )

        if len(operands) < 2:
            raise ValueError(
                "A calculation requires at least two operands."
            )

        operators = operators[:len(operands) - 1]

        if len(operators) != len(operands) - 1:
            raise ValueError(
                "A calculation requires one operator "
                "between each pair of operands."
            )

        return CalculationConfig(
            name=name,
            operands=operands,
            operators=operators,
        )

    # =============================================================
    # CONFIGURATION
    # =============================================================

    def get_transform(self):
        operation = self.operation

        if operation == "__calculate__":
            return self.get_calculation()

        if operation is None:
            raise ValueError(
                "Select an operation."
            )

        columns = self.get_selected_columns()

        if not columns:
            raise ValueError(
                "Select at least one column."
            )

        spec = DataType.TRANSFORM_OPERATIONS.get(
            operation
        )

        if spec is None:
            raise ValueError(
                f"Unsupported operation: {operation}"
            )

        mode = spec.get(
            "mode",
            "single"
        )

        # ---------------------------------------------------------
        # MULTI COLUMN
        # ---------------------------------------------------------

        if mode == "multi":
            value = self.get_operation_value()

            if operation == "one_hot_encoding":
                return MultiColumnTransformConfig(
                    columns=columns,
                    operation=operation,
                    value=value,
                    
                )

            new_column = (
                self.new_col_name.text().strip()
            )

            return MultiColumnTransformConfig(
                columns=columns,
                operation=operation,
                value=value,
                new_column=new_column,
            )

        # ---------------------------------------------------------
        # SINGLE COLUMN
        # ---------------------------------------------------------

        value = self.get_operation_value()

        destination = (
            "new"
            if self.create_col_button.isChecked()
            else "replace"
        )

        new_column = None

        if destination == "new":
            new_column = (
                self.new_col_name.text().strip()
            )

        return TransformConfig(
            column=columns[0],
            operation=operation,
            value=value,
            destination=destination,
            new_column=new_column,
        )
    def get_operands(self):
        operands = []

        for _, combo, constant_edit, _ in self.column_rows:
            data = combo.currentData()

            if not data:
                continue

            operand_type, value = data

            if operand_type == "column":
                operands.append(
                    CalculationOperand(
                        type="column",
                        value=value,
                    )
                )

            elif operand_type == "constant":
                text = constant_edit.text().strip()

                if not text:
                    raise ValueError(
                        "Enter a value for every constant."
                    )

                try:
                    value = float(text)
                except ValueError:
                    raise ValueError(
                        f"Invalid constant: {text}"
                    )

                operands.append(
                    CalculationOperand(
                        type="constant",
                        value=value,
                    )
                )

        return operands

    def get_operation_value(self):
        operation = self.operation

        if operation is None:
            return None

        # -------------------------
        # Type conversion
        # -------------------------
        if operation == "astype":
            return self.type_combo.currentData()

        # -------------------------
        # Numeric value
        # -------------------------
        if operation in {
            "power",
            "modulus",
        }:
            return float(self.value_edit.text())

        # -------------------------
        # Clip
        # -------------------------
        if operation == "clip":
            minimum = self.clip_min.value()
            maximum = self.clip_max.value()

            return {
                "min": minimum,
                "max": maximum,
            }

        # -------------------------
        # Find / replace
        # -------------------------
        if operation == "find_and_replace":
            return {
                "find": self.find_edit.text(),
                "replace": self.replace_edit.text(),
            }
        # -------------------------
        # Replace entire cell
        # -------------------------
        if operation == "replace_all":
            return self.replace_edit.text()
        
        if operation == "replace":
            return {
                "old_value": self.find_edit.text(),
                "new_value": self.replace_edit.text(),
            }



        # -------------------------
        # Regex replacement
        # -------------------------
        if operation in {
            "regex_replace",
            "regex_replace_all",
        }:
            return {
                "pattern": self.pattern_edit.text(),
                "replacement": self.replace_edit.text(),
            }

        # -------------------------
        # String tests/searches
        # -------------------------
        if operation in {
            "contains",
            "startswith",
            "endswith",
            "count_occurrences",
            
        }:
            return self.value_edit.text()

        # -------------------------
        # Regex operations
        # -------------------------
        if operation in {
            "regex_extract",
            "regex_match",
            "regex_findall",
        }:
            return self.pattern_edit.text()

        # -------------------------
        # Substring
        # -------------------------
        if operation in {
            "substring",
            "extract_substring",
        }:
            return {
                "start": self.substring_start.value(),
                "end": self.substring_end.value(),
            }

        # -------------------------
        # Padding
        # -------------------------
        if operation == "pad":
            return self.pad_width.value()

        # -------------------------
        # Concatenation
        # -------------------------
        if operation == "concatenate":
            return self.separator_edit.text()

        return None

    # =============================================================
    # PREVIEW
    # =============================================================

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

            result = self.processor.apply_transform(
                self.operation_dataframe,
                config
            )

            if (
                self.use_selection.isChecked()
                and self.preserve_unselected.isChecked()
            ):
                result = self.merge_selection_result(
                    self.dataframe,
                    result
                )

            self.result_preview.display_dataframe(
                result,
                full=full
            )

            self.result = result
            self.apply_button.setEnabled(True)

        except (
            KeyError,
            TypeError,
            ValueError,
            ZeroDivisionError,
        ):
            self.result_preview.clearContents()
            self.result_preview.setRowCount(0)
            self.apply_button.setEnabled(False)

    # =============================================================
    # APPLY
    # =============================================================

    def apply(self):
        try:
            config = self.get_transform()

            operation_result = (
                self.processor.apply_transform(
                    self.operation_dataframe,
                    config
                )
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
            ValueError,
            ZeroDivisionError,
        ) as error:

            QMessageBox.warning(
                self,
                "Transform Failed",
                str(error)
            )

    # =============================================================
    # DESTINATION HELPERS
    # =============================================================

    def default_new_column_name(self):
        columns = self.get_selected_columns()
        operation = self.operation

        if not columns or operation is None:
            return ""

        if operation == "__calculate__":
            return "calculated"

        if len(columns) > 1:
            return (
                "_".join(map(str, columns))
                + "_"
                + operation
            )

        column = columns[0]

        suffixes = {
            "normalize": "normalized",
            "absolute": "absolute",
            "round": "rounded",
            "round_to": "rounded",
            "standardize": "standardized",
            "rank": "rank",
            "log": "log",
            "exp": "exp",
            "sqrt": "sqrt",
            "cbrt": "cbrt",
            "reciprocal": "reciprocal",
            "square": "square",
            "cube": "cube",
            "power": "power",
            "modulus": "modulus",
            "floor": "floor",
            "ceil": "ceil",
            "clip": "clip",
            "cumulative_sum": "cumsum",
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
            "extract_second": "second",
            "extract_millisecond": "millisecond",
            "extract_nanosecond": "nanosecond",
            "astype": "converted",
        }

        suffix = suffixes.get(
            operation,
            operation
        )

        return f"{column}_{suffix}"

    # =============================================================
    # SELECTION MERGE
    # =============================================================

    def merge_selection_result(
        self,
        original,
        result,
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

    # =============================================================
    # RESULT
    # =============================================================

    def get_result(self):
        return self.result

    def update_operator_rows(self):
        is_calculation = (
            self.operation == "__calculate__"
        )

        count = len(self.column_rows)

        for index, (
            _,
            combo,
            constant_edit,
            operator_combo,
            _,
        ) in enumerate(self.column_rows):

            data = combo.currentData()

            is_constant = (
                data is not None
                and data[0] == "constant"
            )

            constant_edit.setVisible(
                is_calculation
                and is_constant
            )

            operator_combo.setVisible(
                is_calculation
                and index < count - 1
            )
            
    def update_column_rows_for_operation(self):
        is_calculation = (
            self.operation == "__calculate__"
        )

        if is_calculation:
            self.source_label.setText(
                "Calculation operands"
            )
        else:
            self.source_label.setText(
                "Source columns"
            )

        for (
            _,
            combo,
            constant_edit,
            operator_combo,
            _,
        ) in self.column_rows:

            data = combo.currentData()

            is_constant = (
                data is not None
                and data[0] == "constant"
            )

            # Constants are only valid for calculations
            if not is_calculation and is_constant:
                combo.setCurrentIndex(0)
                constant_edit.clear()

            constant_edit.setVisible(
                is_calculation
                and is_constant
            )

        self.update_operator_rows()