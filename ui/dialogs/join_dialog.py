from PySide6.QtCore import Qt
import pandas as pd
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget
)

from core.condition_group import ConditionGroup
from core.data_processor import JoinConfig
from ui.helpers.condition_row import ConditionRow
from ui.table.preview_table import PreviewTable


class JoinDialog(QDialog):
    """Configure a join between the main and result datasets."""

    def __init__(self, left_dataframe, right_dataframe, parent=None,
                 target_dataframes=None, target="main"):
        super().__init__(parent)
        self.target_dataframes = target_dataframes or {target: left_dataframe}
        self.left_dataframe = left_dataframe
        self.right_dataframe = right_dataframe
        self.preview = PreviewTable()
        self.imported_preview = PreviewTable()
        self.result_preview = PreviewTable()
        self.column_checks = []
        self.filter_rows = []
        self.left_column_checks = []
        self.right_column_checks = []
        self.setWindowTitle("Join Data")
        layout = QVBoxLayout(self)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Target dataset"))
        self.target_combo = QComboBox()
        for key, label in (("main", "Main Dataset"),
                           ("result", "Result Dataset")):
            if key in self.target_dataframes:
                self.target_combo.addItem(label, key)
        self.target_combo.setCurrentIndex(
            max(0, self.target_combo.findData(target))
        )
        controls.addWidget(self.target_combo)
        self.use_selection = QCheckBox("Use selection")


        controls.addWidget(
            self.use_selection
        )
        controls.addWidget(QLabel("Output"))
        self.output_combo = QComboBox()
        self.output_combo.addItem("Create result dataset", "result")
        self.output_combo.addItem("Add columns to target", "target")
        self.output_combo.addItem("Concatenate rows", "concat")
        controls.addWidget(self.output_combo)

        self.ignore_index_check = QCheckBox("Ignore index")
        controls.addWidget(self.ignore_index_check)

        controls.addWidget(QLabel("Group key"))
        self.group_key_combo = QComboBox()
        self.group_key_combo.addItem("None", None)
        for column in right_dataframe.columns:
            self.group_key_combo.addItem(str(column), column)
        controls.addWidget(self.group_key_combo)

        controls.addWidget(QLabel("Main key"))
        self.left_key_combo = QComboBox()
        for column in left_dataframe.columns:
            self.left_key_combo.addItem(str(column), column)
        controls.addWidget(self.left_key_combo)

        controls.addWidget(QLabel("Result key"))
        self.right_key_combo = QComboBox()
        for column in right_dataframe.columns:
            self.right_key_combo.addItem(str(column), column)
        controls.addWidget(self.right_key_combo)

        controls.addWidget(QLabel("Type"))
        self.join_type_combo = QComboBox()
        for label, value in (
            ("Inner", "inner"),
            ("Left", "left"),
            ("Right", "right"),
            ("Outer", "outer")
        ):
            self.join_type_combo.addItem(label, value)
        controls.addWidget(self.join_type_combo)
        layout.addLayout(controls)

        layout.addWidget(QLabel("Columns to include"))

        columns_layout = QHBoxLayout()

        # =====================================
        # Main dataset
        # =====================================

        main_group = QGroupBox("Main Dataset")

        self.main_columns_layout = QGridLayout()
        main_group.setLayout(
            self.main_columns_layout
        )

        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setWidget(main_group)

        # =====================================
        # Imported dataset
        # =====================================

        imported_group = QGroupBox("Imported Dataset")

        self.imported_columns_layout = QGridLayout()
        imported_group.setLayout(
            self.imported_columns_layout
        )

        imported_scroll = QScrollArea()
        imported_scroll.setWidgetResizable(True)
        imported_scroll.setWidget(imported_group)

        columns_layout.addWidget(main_scroll)
        columns_layout.addWidget(imported_scroll)

        layout.addLayout(columns_layout)

        #self._build_column_checks()

        self.filter_toggle = QCheckBox("Filter imported rows")
        layout.addWidget(self.filter_toggle)
        self.filter_logic_combo = QComboBox()
        self.filter_logic_combo.addItem("Match all (AND)", "AND")
        self.filter_logic_combo.addItem("Match any (OR)", "OR")
        layout.addWidget(self.filter_logic_combo)
        self.filter_layout = QVBoxLayout()
        layout.addLayout(self.filter_layout)
        self.add_filter_button = QPushButton("+ Add Imported Row Filter")
        layout.addWidget(self.add_filter_button)

        previews = QSplitter(Qt.Horizontal)
        previews.addWidget(self.preview)
        previews.addWidget(self.imported_preview)
        previews.addWidget(self.result_preview)
        layout.addWidget(previews)

        preview_labels = QHBoxLayout()
        preview_labels.addWidget(QLabel("Main dataset"))
        preview_labels.addWidget(QLabel("Imported dataset"))
        preview_labels.addWidget(QLabel("Joined preview"))
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
        self.left_key_combo.currentIndexChanged.connect(self.update_preview)
        self.right_key_combo.currentIndexChanged.connect(self.update_preview)
        self.join_type_combo.currentIndexChanged.connect(self.update_preview)
        self.target_combo.currentIndexChanged.connect(self.change_target)
        self.output_combo.currentIndexChanged.connect(self.update_preview)
        self.output_combo.currentIndexChanged.connect(
            self.update_output_controls
        )
        self.ignore_index_check.toggled.connect(self.update_preview)
        self.group_key_combo.currentIndexChanged.connect(self.update_preview)
        self.filter_toggle.toggled.connect(self.update_filter_controls)
        self.filter_logic_combo.currentIndexChanged.connect(self.update_preview)
        self.add_filter_button.clicked.connect(self.create_filter_row)
        self.change_target()
        self.update_output_controls()
        self.create_filter_row()
        self.update_filter_controls()
        self.update_preview()

    def get_config(self):
        return JoinConfig(
            left_key=self.left_key_combo.currentData(),
            right_key=self.right_key_combo.currentData(),
            join_type=self.join_type_combo.currentData(),
            mode=self.output_combo.currentData(),
            ignore_index=self.ignore_index_check.isChecked(),
            group_key=self.group_key_combo.currentData(),
            left_columns=self.get_selected_left_columns(),
            right_columns=self.get_selected_right_columns(),
            filter_conditions=self.get_filter_conditions()
        )

    def get_target(self):
        return self.target_combo.currentData()

    def get_output(self):
        return self.output_combo.currentData()

    def update_output_controls(self):
        is_concat = self.output_combo.currentData() == "concat"
        self.left_key_combo.setEnabled(not is_concat)
        self.right_key_combo.setEnabled(not is_concat)
        self.join_type_combo.setEnabled(not is_concat)
        self.group_key_combo.setEnabled(not is_concat)

    def _build_column_checks(self):
        """Build the column selectors for both datasets."""

        self._clear_column_layout(
            self.main_columns_layout
        )

        self._clear_column_layout(
            self.imported_columns_layout
        )

        self.left_column_checks.clear()
        self.right_column_checks.clear()

        # =====================================
        # Main dataset
        # =====================================

        for index, column in enumerate(
            self.left_dataframe.columns
        ):

            checkbox = QCheckBox(str(column))
            checkbox.setChecked(True)

            checkbox.stateChanged.connect(
                self.update_preview
            )

            row = index // 3
            column_index = index % 3

            self.main_columns_layout.addWidget(
                checkbox,
                row,
                column_index
            )

            self.left_column_checks.append(
                (column, checkbox)
            )

        # =====================================
        # Imported dataset
        # =====================================

        for index, column in enumerate(
            self.right_dataframe.columns
        ):

            checkbox = QCheckBox(str(column))
            checkbox.setChecked(True)

            checkbox.stateChanged.connect(
                self.update_preview
            )

            row = index // 3
            column_index = index % 3

            self.imported_columns_layout.addWidget(
                checkbox,
                row,
                column_index
            )

            self.right_column_checks.append(
                (column, checkbox)
            )

        self.ensure_key_selected()

    def ensure_key_selected(self):
        """Ensure both join keys remain selected."""

        left_key = self.left_key_combo.currentData()
        right_key = self.right_key_combo.currentData()

        for column, checkbox in self.left_column_checks:
            is_key = column == left_key
            checkbox.setEnabled(not is_key)

            if is_key:
                checkbox.setChecked(True)

        for column, checkbox in self.right_column_checks:
            is_key = column == right_key
            checkbox.setEnabled(not is_key)

            if is_key:
                checkbox.setChecked(True)

    def get_selected_columns(self):
        selected = [
            column for column, checkbox in self.column_checks
            if checkbox.isChecked()
        ]
        key = self.right_key_combo.currentData()
        if key is not None and key not in selected:
            selected.insert(0, key)
        return selected

    def update_filter_controls(self):
        enabled = self.filter_toggle.isChecked()
        self.filter_logic_combo.setVisible(enabled)
        self.add_filter_button.setVisible(enabled)
        for index in range(self.filter_layout.count()):
            widget = self.filter_layout.itemAt(index).widget()
            if widget:
                widget.setVisible(enabled)
        self.update_preview()

    def create_filter_row(self):
        row = ConditionRow(self.right_dataframe)
        row.remove_requested.connect(self.remove_filter_row)
        row.column_combo.currentIndexChanged.connect(self.update_preview)
        row.operator_combo.currentIndexChanged.connect(self.update_preview)
        row.value_input.textChanged.connect(self.update_preview)
        self.filter_layout.addWidget(row)
        self.filter_rows.append(row)

    def remove_filter_row(self, row):
        if len(self.filter_rows) <= 1:
            return
        self.filter_rows.remove(row)
        self.filter_layout.removeWidget(row)
        row.deleteLater()
        self.update_preview()

    def get_filter_conditions(self):
        if not self.filter_toggle.isChecked():
            return None
        return ConditionGroup(
            [row.get_condition() for row in self.filter_rows],
            self.filter_logic_combo.currentData()
        )

    def change_target(self):
        if not hasattr(self, "left_key_combo"):
            return
        self.left_dataframe = self.target_dataframes[self.get_target()]
        self.left_key_combo.clear()
        for column in self.left_dataframe.columns:
            self.left_key_combo.addItem(str(column), column)
        self._build_column_checks()
        self.update_preview()

    def update_preview(self):

        full = self.show_all_rows.isChecked()

        try:
            # ==================================
            # Main dataset
            # ==================================

            left_dataframe = self.left_dataframe

            selected_left = self.get_selected_left_columns()

            if selected_left:
                left_dataframe = left_dataframe.loc[
                    :,
                    selected_left
                ]

            self.preview.display_dataframe(
                left_dataframe,
                full=full
            )

            # ==================================
            # Imported dataset
            # ==================================

            right_dataframe = self.right_dataframe

            conditions = self.get_filter_conditions()

            if conditions is not None:
                right_dataframe = right_dataframe[
                    conditions.evaluate(right_dataframe)
                ]

            group_key = self.group_key_combo.currentData()

            if group_key is not None:
                right_dataframe = right_dataframe.drop_duplicates(
                    subset=[group_key],
                    keep="first"
                )

            selected_right = self.get_selected_right_columns()

            if selected_right:
                right_dataframe = right_dataframe.loc[
                    :,
                    selected_right
                ]

            self.imported_preview.display_dataframe(
                right_dataframe,
                full=full
            )

            # ==================================
            # Joined preview
            # ==================================

            if self.output_combo.currentData() == "concat":

                result = pd.concat(
                    [
                        left_dataframe,
                        right_dataframe
                    ],
                    ignore_index=self.ignore_index_check.isChecked()
                )

            else:

                result = left_dataframe.merge(
                    right_dataframe,
                    left_on=self.left_key_combo.currentData(),
                    right_on=self.right_key_combo.currentData(),
                    how=self.join_type_combo.currentData()
                )

            self.result_preview.display_dataframe(
                result,
                full=full
            )

            self.apply_button.setEnabled(True)

        except (KeyError, TypeError, ValueError):

            self.result_preview.clearContents()
            self.result_preview.setRowCount(0)

            self.apply_button.setEnabled(False)

    def _clear_column_layout(self, layout):
        """Remove all widgets from a column layout."""

        while layout.count():

            item = layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def get_selected_left_columns(self):
        selected = [
            column
            for column, checkbox in self.left_column_checks
            if checkbox.isChecked()
        ]

        key = self.left_key_combo.currentData()

        if key is not None and key not in selected:
            selected.insert(0, key)

        return selected


    def get_selected_right_columns(self):
        selected = [
            column
            for column, checkbox in self.right_column_checks
            if checkbox.isChecked()
        ]

        key = self.right_key_combo.currentData()

        if key is not None and key not in selected:
            selected.insert(0, key)

        return selected