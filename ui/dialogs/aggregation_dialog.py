from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout
)

from core.aggregation import Aggregation
from core.data_processor import DataProcessor
from ui.helpers.aggregation_row import AggregationRow
from ui.helpers.groupby_row import GroupbyRow
from ui.table.preview_table import PreviewTable


class AggregationDialog(QDialog):
    """Configure an aggregation with target selection and live preview."""

    def __init__(self, dataframe, parent=None, target_dataframes=None,
                 target="main"):
        super().__init__(parent)
        self.dataframe = dataframe
        if target_dataframes is None:
            self.target_dataframes = {target: dataframe}
        else:
            self.target_dataframes = target_dataframes
        self.groupby_rows = []
        self.aggregation_rows = []
        self.processor = DataProcessor()
        self.source_preview = PreviewTable()
        self.result_preview = PreviewTable()

        self.setWindowTitle("Aggregate Data")
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
        self.use_selection = QCheckBox("Use selection")


        target_layout.addWidget(
            self.use_selection
        )
        target_layout.addWidget(self.target_combo)
        layout.addLayout(target_layout)

        layout.addWidget(QLabel("Group By"))
        self.groupby_layout = QVBoxLayout()
        layout.addLayout(self.groupby_layout)
        self.add_group_button = QPushButton("+ Add Group")
        layout.addWidget(self.add_group_button)

        layout.addWidget(QLabel("Aggregations"))
        self.aggregation_layout = QVBoxLayout()
        layout.addLayout(self.aggregation_layout)
        self.add_aggregation_button = QPushButton("+ Add Aggregation")
        layout.addWidget(self.add_aggregation_button)

        previews = QSplitter(Qt.Horizontal)
        previews.addWidget(self.source_preview)
        previews.addWidget(self.result_preview)
        layout.addWidget(previews)
        labels = QHBoxLayout()
        labels.addWidget(QLabel("Target data"))
        labels.addWidget(QLabel("Aggregation result"))
        
        layout.insertLayout(layout.indexOf(previews), labels)
        self.show_all_rows = QCheckBox("Show all rows")
        self.show_all_rows.toggled.connect(self.update_preview)
        layout.addWidget(self.show_all_rows)
        buttons = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        self.apply_button = QPushButton("Apply")
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(self.apply_button)
        layout.addLayout(buttons)

        cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.accept)
        self.add_group_button.clicked.connect(self.create_groupby_row)
        self.add_aggregation_button.clicked.connect(self.create_aggregation_row)
        self.target_combo.currentIndexChanged.connect(self.change_target)

        self.change_target()
        self.update_preview()

    def get_target(self):
        return self.target_combo.currentData()

    def change_target(self):
        if not hasattr(self, "groupby_layout"):
            return
        self.dataframe = self.target_dataframes[self.get_target()]
        self._clear_rows()
        self.create_groupby_row()
        self.create_aggregation_row()
        self.update_preview()

    def _clear_rows(self):
        for layout, rows in (
            (self.groupby_layout, self.groupby_rows),
            (self.aggregation_layout, self.aggregation_rows)
        ):
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            rows.clear()

    def create_groupby_row(self):
        row = GroupbyRow(self.dataframe)
        row.remove_requested.connect(self.remove_groupby_row)
        row.column_combo.currentIndexChanged.connect(self.update_preview)
        self.groupby_layout.addWidget(row)
        self.groupby_rows.append(row)

    def remove_groupby_row(self, row):
        if len(self.groupby_rows) <= 1:
            return
        self.groupby_rows.remove(row)
        self.groupby_layout.removeWidget(row)
        row.deleteLater()
        self.update_preview()

    def create_aggregation_row(self):
        row = AggregationRow(self.dataframe)
        row.remove_requested.connect(self.remove_aggregation_row)
        row.column_combo.currentIndexChanged.connect(self.update_preview)
        row.function_combo.currentIndexChanged.connect(self.update_preview)
        self.aggregation_layout.addWidget(row)
        self.aggregation_rows.append(row)

    def remove_aggregation_row(self, row):
        if len(self.aggregation_rows) <= 1:
            return
        self.aggregation_rows.remove(row)
        self.aggregation_layout.removeWidget(row)
        row.deleteLater()
        self.update_preview()

    def get_aggregation(self):
        return Aggregation(
            [row.get_column() for row in self.groupby_rows],
            [row.get_aggregation() for row in self.aggregation_rows]
        )

    def update_preview(self):
        # Preview uses the same processor validation as Apply, so the dialog
        # cannot display a result that the main window would later reject.
        full = self.show_all_rows.isChecked()
        
        self.source_preview.display_dataframe(self.dataframe,full = full)
        try:
            result = self.processor.aggregate(
                self.dataframe,
                self.get_aggregation()
            )
        except (KeyError, TypeError, ValueError):
            self.result_preview.clearContents()
            self.result_preview.setRowCount(0)
            self.apply_button.setEnabled(False)
            return

        self.result_preview.display_dataframe(result, full=full)
        self.apply_button.setEnabled(True)
