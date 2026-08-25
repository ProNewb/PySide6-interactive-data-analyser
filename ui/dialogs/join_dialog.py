import pandas as pd

from PySide6.QtCore import Qt
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
    QVBoxLayout
)

from core.condition_group import ConditionGroup
from core.data_processor import JoinConfig
from ui.helpers.condition_row import ConditionRow
from ui.table.preview_table import PreviewTable


class JoinDialog(QDialog):

    def __init__(
        self,
        datasets,
        parent=None,
        current=None,
        use_selection=False
    ):
        super().__init__(parent)

        self.datasets = datasets

        # --------------------------------------------------
        # Data
        # --------------------------------------------------

        self.left_dataframe = None
        self.right_dataframe = None

        # --------------------------------------------------
        # UI state
        # --------------------------------------------------

        self.left_column_checks = []
        self.right_column_checks = []
        self.filter_rows = []

        # --------------------------------------------------
        # Previews
        # --------------------------------------------------

        self.preview = PreviewTable()
        self.imported_preview = PreviewTable()
        self.result_preview = PreviewTable()

        # --------------------------------------------------
        # Window
        # --------------------------------------------------

        self.setWindowTitle("Join Data")

        layout = QVBoxLayout(self)

        # ==================================================
        # Dataset selection
        # ==================================================

        dataset_controls = QHBoxLayout()

        dataset_controls.addWidget(
            QLabel("Left dataset")
        )

        self.left_dataset_combo = QComboBox()

        for name in datasets:
            self.left_dataset_combo.addItem(
                name
            )

        if current:
            index = self.left_dataset_combo.findText(current)

            if index >= 0:
                self.left_dataset_combo.setCurrentIndex(index)

        dataset_controls.addWidget(
            self.left_dataset_combo
        )

        # --------------------------------------------------

        dataset_controls.addWidget(
            QLabel("Right dataset")
        )

        self.right_dataset_combo = QComboBox()

        for name in datasets:
            self.right_dataset_combo.addItem(
                name
            )

        # Try to choose a different dataset on the right
        if self.right_dataset_combo.count() > 1:

            right_index = 1

            if (
                current
                and self.right_dataset_combo.currentText() == current
            ):
                right_index = 0

            self.right_dataset_combo.setCurrentIndex(
                right_index
            )

        dataset_controls.addWidget(
            self.right_dataset_combo
        )

        layout.addLayout(
            dataset_controls
        )

        # ==================================================
        # Selection controls
        # ==================================================

        selection_controls = QHBoxLayout()

        self.left_use_selection = QCheckBox(
            "Use left selection"
        )

        self.right_use_selection = QCheckBox(
            "Use right selection"
        )

        # Preserve the old global Use Selection state
        self.left_use_selection.setChecked(
            use_selection
        )

        self.right_use_selection.setChecked(
            False
        )

        selection_controls.addWidget(
            self.left_use_selection
        )

        selection_controls.addWidget(
            self.right_use_selection
        )

        selection_controls.addStretch()

        layout.addLayout(
            selection_controls
        )

        # ==================================================
        # Join controls
        # ==================================================

        controls = QHBoxLayout()

        # Output
        controls.addWidget(
            QLabel("Output")
        )

        self.output_combo = QComboBox()

        self.output_combo.addItem(
            "Create result dataset",
            "result"
        )

        self.output_combo.addItem(
            "Add columns to target",
            "target"
        )

        self.output_combo.addItem(
            "Concatenate rows",
            "concat"
        )

        controls.addWidget(
            self.output_combo
        )

        # Ignore index
        self.ignore_index_check = QCheckBox(
            "Ignore index"
        )

        controls.addWidget(
            self.ignore_index_check
        )

       
        # Left key
        controls.addWidget(
            QLabel("Left key")
        )

        self.left_key_combo = QComboBox()

        controls.addWidget(
            self.left_key_combo
        )

        # Right key
        controls.addWidget(
            QLabel("Right key")
        )

        self.right_key_combo = QComboBox()

        controls.addWidget(
            self.right_key_combo
        )

        # Join type
        controls.addWidget(
            QLabel("Type")
        )

        self.join_type_combo = QComboBox()

        for label, value in (
            ("Inner", "inner"),
            ("Left", "left"),
            ("Right", "right"),
            ("Outer", "outer")
        ):
            self.join_type_combo.addItem(
                label,
                value
            )

        controls.addWidget(
            self.join_type_combo
        )

        layout.addLayout(
            controls
        )

        # ==================================================
        # Column selection
        # ==================================================

        layout.addWidget(
            QLabel("Columns to include")
        )

        columns_layout = QHBoxLayout()

        # --------------------------------------------------
        # Left columns
        # --------------------------------------------------

        left_group = QGroupBox(
            "Left Dataset"
        )

        self.main_columns_layout = QGridLayout()

        left_group.setLayout(
            self.main_columns_layout
        )

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setWidget(left_group)

        # --------------------------------------------------
        # Right columns
        # --------------------------------------------------

        right_group = QGroupBox(
            "Right Dataset"
        )

        self.imported_columns_layout = QGridLayout()

        right_group.setLayout(
            self.imported_columns_layout
        )

        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(right_group)

        columns_layout.addWidget(
            left_scroll
        )

        columns_layout.addWidget(
            right_scroll
        )

        layout.addLayout(
            columns_layout
        )

        # ==================================================
        # Right-side filtering
        # ==================================================

        self.filter_toggle = QCheckBox(
            "Filter right dataset rows"
        )

        layout.addWidget(
            self.filter_toggle
        )

        self.filter_logic_combo = QComboBox()

        self.filter_logic_combo.addItem(
            "Match all (AND)",
            "AND"
        )

        self.filter_logic_combo.addItem(
            "Match any (OR)",
            "OR"
        )

        layout.addWidget(
            self.filter_logic_combo
        )

        self.filter_layout = QVBoxLayout()

        layout.addLayout(
            self.filter_layout
        )

        self.add_filter_button = QPushButton(
            "+ Add Right Dataset Filter"
        )

        layout.addWidget(
            self.add_filter_button
        )

        # ==================================================
        # Previews
        # ==================================================

        previews = QSplitter(
            Qt.Horizontal
        )

        previews.addWidget(
            self.preview
        )

        previews.addWidget(
            self.imported_preview
        )

        previews.addWidget(
            self.result_preview
        )

        preview_labels = QHBoxLayout()

        preview_labels.addWidget(
            QLabel("Left dataset")
        )

        preview_labels.addWidget(
            QLabel("Right dataset")
        )

        preview_labels.addWidget(
            QLabel("Joined preview")
        )

        self.show_all_rows = QCheckBox(
            "Show all rows"
        )

        preview_labels.addWidget(
            self.show_all_rows
        )

        layout.addLayout(
            preview_labels
        )

        layout.addWidget(
            previews
        )

        # ==================================================
        # Buttons
        # ==================================================

        buttons = QHBoxLayout()

        cancel_button = QPushButton(
            "Cancel"
        )

        self.apply_button = QPushButton(
            "Apply"
        )

        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(self.apply_button)

        layout.addLayout(
            buttons
        )

        # ==================================================
        # Signals
        # ==================================================

        cancel_button.clicked.connect(
            self.reject
        )

        self.apply_button.clicked.connect(
            self.accept
        )

        self.left_dataset_combo.currentIndexChanged.connect(
            self.change_datasets
        )

        self.right_dataset_combo.currentIndexChanged.connect(
            self.change_datasets
        )

        self.left_use_selection.toggled.connect(
            self.change_datasets
        )

        self.right_use_selection.toggled.connect(
            self.change_datasets
        )

        self.left_key_combo.currentIndexChanged.connect(
            self.update_preview
        )

        self.right_key_combo.currentIndexChanged.connect(
            self.update_preview
        )

        self.join_type_combo.currentIndexChanged.connect(
            self.update_preview
        )

        self.output_combo.currentIndexChanged.connect(
            self.update_output_controls
        )

        self.output_combo.currentIndexChanged.connect(
            self.update_preview
        )

        self.ignore_index_check.toggled.connect(
            self.update_preview
        )

        self.filter_toggle.toggled.connect(
            self.update_filter_controls
        )

        self.filter_logic_combo.currentIndexChanged.connect(
            self.update_preview
        )

        self.add_filter_button.clicked.connect(
            self.create_filter_row
        )

        self.show_all_rows.toggled.connect(
            self.update_preview
        )

        # ==================================================
        # Initial state
        # ==================================================

        self.change_datasets()

        self.update_output_controls()

        self.create_filter_row()

        self.update_filter_controls()

    # ======================================================
    # Dataset handling
    # ======================================================

    def get_left_dataframe(self):

        key = self.left_dataset_combo.currentText()

        if key not in self.datasets:
            return None

        info = self.datasets[key]

        dataframe = info.get("dataframe")

        if dataframe is None:
            return None

        if self.left_use_selection.isChecked():

            view = info.get("view")

            if view is not None:
                selected = view.get_analysis_dataframe()

                if selected is not None:
                    return selected

        return dataframe

    # ------------------------------------------------------

    def get_right_dataframe(self):

        key = self.right_dataset_combo.currentText()

        if key not in self.datasets:
            return None

        info = self.datasets[key]

        dataframe = info.get("dataframe")

        if dataframe is None:
            return None

        if self.right_use_selection.isChecked():

            view = info.get("view")

            if view is not None:
                selected = view.get_analysis_dataframe()

                if selected is not None:
                    return selected

        return dataframe

    # ------------------------------------------------------

    def get_workspace(self):

        key = self.left_dataset_combo.currentText()

        if key not in self.datasets:
            return None

        return self.datasets[key].get(
            "workspace"
        )

    # ------------------------------------------------------

    def get_target(self):

        key = self.left_dataset_combo.currentText()

        if key not in self.datasets:
            return None

        return self.datasets[key].get(
            "target"
        )

    # ======================================================
    # Dataset changed
    # ======================================================

    def change_datasets(self):

        self.left_dataframe = (
            self.get_left_dataframe()
        )

        self.right_dataframe = (
            self.get_right_dataframe()
        )

        if (
            self.left_dataframe is None
            or self.right_dataframe is None
        ):
            self.apply_button.setEnabled(
                False
            )

            return

        self._build_column_checks()

        self.populate_join_combos()

        self.update_preview()

    # ======================================================
    # Column selectors
    # ======================================================

    def _build_column_checks(self):

        self._clear_column_layout(
            self.main_columns_layout
        )

        self._clear_column_layout(
            self.imported_columns_layout
        )

        self.left_column_checks.clear()
        self.right_column_checks.clear()

        # --------------------------------------------------
        # Left
        # --------------------------------------------------

        for index, column in enumerate(
            self.left_dataframe.columns
        ):

            checkbox = QCheckBox(
                str(column)
            )

            checkbox.setChecked(
                True
            )

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

        # --------------------------------------------------
        # Right
        # --------------------------------------------------

        for index, column in enumerate(
            self.right_dataframe.columns
        ):

            checkbox = QCheckBox(
                str(column)
            )

            checkbox.setChecked(
                True
            )

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

    # ======================================================
    # Join keys
    # ======================================================

    def populate_join_combos(self):

        self.left_key_combo.blockSignals(True)
        self.right_key_combo.blockSignals(True)


        self.left_key_combo.clear()
        self.right_key_combo.clear()


        # --------------------------------------------------
        # Left keys
        # --------------------------------------------------

        for column in self.left_dataframe.columns:

            self.left_key_combo.addItem(
                str(column),
                column
            )

        # --------------------------------------------------
        # Right keys
        # --------------------------------------------------

        for column in self.right_dataframe.columns:

            self.right_key_combo.addItem(
                str(column),
                column
            )

        self.left_key_combo.blockSignals(False)
        self.right_key_combo.blockSignals(False)


    # ======================================================
    # Selected columns
    # ======================================================

    def get_selected_left_columns(self):

        selected = [
            column
            for column, checkbox
            in self.left_column_checks
            if checkbox.isChecked()
        ]

        key = self.left_key_combo.currentData()

        if (
            key is not None
            and key not in selected
        ):
            selected.insert(
                0,
                key
            )

        return selected

    # ------------------------------------------------------

    def get_selected_right_columns(self):

        selected = [
            column
            for column, checkbox
            in self.right_column_checks
            if checkbox.isChecked()
        ]

        key = self.right_key_combo.currentData()

        if (
            key is not None
            and key not in selected
        ):
            selected.insert(
                0,
                key
            )

        return selected

    # ======================================================
    # Filters
    # ======================================================

    def create_filter_row(self):

        if self.right_dataframe is None:
            return

        row = ConditionRow(
            self.right_dataframe
        )

        row.remove_requested.connect(
            self.remove_filter_row
        )

        row.column_combo.currentIndexChanged.connect(
            self.update_preview
        )

        row.operator_combo.currentIndexChanged.connect(
            self.update_preview
        )

        row.value_input.textChanged.connect(
            self.update_preview
        )

        self.filter_layout.addWidget(
            row
        )

        self.filter_rows.append(
            row
        )

    # ------------------------------------------------------

    def remove_filter_row(self, row):

        if len(self.filter_rows) <= 1:
            return

        self.filter_rows.remove(
            row
        )

        self.filter_layout.removeWidget(
            row
        )

        row.deleteLater()

        self.update_preview()

    # ------------------------------------------------------

    def get_filter_conditions(self):

        if not self.filter_toggle.isChecked():
            return None

        return ConditionGroup(
            [
                row.get_condition()
                for row in self.filter_rows
            ],
            self.filter_logic_combo.currentData()
        )

    # ------------------------------------------------------

    def update_filter_controls(self):

        enabled = (
            self.filter_toggle.isChecked()
        )

        self.filter_logic_combo.setVisible(
            enabled
        )

        self.add_filter_button.setVisible(
            enabled
        )

        for index in range(
            self.filter_layout.count()
        ):

            widget = (
                self.filter_layout
                .itemAt(index)
                .widget()
            )

            if widget:
                widget.setVisible(
                    enabled
                )

        self.update_preview()

    # ======================================================
    # Output controls
    # ======================================================

    def update_output_controls(self):

        is_concat = (
            self.output_combo.currentData()
            == "concat"
        )

        self.left_key_combo.setEnabled(
            not is_concat
        )

        self.right_key_combo.setEnabled(
            not is_concat
        )

        self.join_type_combo.setEnabled(
            not is_concat
        )

    # ======================================================
    # Preview
    # ======================================================

    def update_preview(self):

        if (
            self.left_dataframe is None
            or self.right_dataframe is None
        ):
            self.apply_button.setEnabled(
                False
            )

            return

        full = (
            self.show_all_rows.isChecked()
        )

        try:

            # ==============================================
            # LEFT
            # ==============================================

            left_dataframe = (
                self.left_dataframe
            )

            selected_left = (
                self.get_selected_left_columns()
            )

            if selected_left:
                left_dataframe = (
                    left_dataframe.loc[
                        :,
                        selected_left
                    ]
                )

            self.preview.display_dataframe(
                left_dataframe,
                full=full
            )

            # ==============================================
            # RIGHT
            # ==============================================

            right_dataframe = (
                self.right_dataframe
            )

            conditions = (
                self.get_filter_conditions()
            )

            if conditions is not None:

                right_dataframe = (
                    right_dataframe[
                        conditions.evaluate(
                            right_dataframe
                        )
                    ]
                )


            selected_right = (
                self.get_selected_right_columns()
            )

            if selected_right:

                right_dataframe = (
                    right_dataframe.loc[
                        :,
                        selected_right
                    ]
                )

            self.imported_preview.display_dataframe(
                right_dataframe,
                full=full
            )

            # ==============================================
            # RESULT
            # ==============================================

            if self.output_combo.currentData() == "concat":

                result = pd.concat(
                    [
                        left_dataframe,
                        right_dataframe
                    ],
                    ignore_index=(
                        self.ignore_index_check.isChecked()
                    )
                )

            else:

                left_key = (
                    self.left_key_combo.currentData()
                )

                right_key = (
                    self.right_key_combo.currentData()
                )

                if (
                    left_key is None
                    or right_key is None
                ):
                    raise ValueError(
                        "Both join keys must be selected."
                    )

                result = left_dataframe.merge(
                    right_dataframe,
                    left_on=left_key,
                    right_on=right_key,
                    how=self.join_type_combo.currentData()
                )

            self.result_preview.display_dataframe(
                result,
                full=full
            )

            self.apply_button.setEnabled(
                True
            )

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            self.result_preview.clearContents()
            self.result_preview.setRowCount(
                0
            )

            self.apply_button.setEnabled(
                False
            )

    # ======================================================
    # Config
    # ======================================================

    def get_config(self):

        return JoinConfig(
            left_key=self.left_key_combo.currentData(),

            right_key=self.right_key_combo.currentData(),

            join_type=self.join_type_combo.currentData(),

            mode=self.output_combo.currentData(),

            ignore_index=(
                self.ignore_index_check.isChecked()
            ),

            left_columns=(
                self.get_selected_left_columns()
            ),

            right_columns=(
                self.get_selected_right_columns()
            ),

            filter_conditions=(
                self.get_filter_conditions()
            )
        )

    # ======================================================
    # Helpers
    # ======================================================

    def _clear_column_layout(self, layout):

        while layout.count():

            item = layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()