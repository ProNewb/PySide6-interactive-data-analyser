from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton
)

from views.ui.groupby_row import GroupbyRow
from views.ui.aggregation_row import AggregationRow
from core.aggregation import Aggregation


class AggregationDialog(QDialog):

    def __init__(self, dataframe, parent=None):

        super().__init__(parent)

        self.dataframe = dataframe

        self.groupby_rows = []
        self.aggregation_rows = []

        self.setWindowTitle("Aggregate Data")

        layout = QVBoxLayout()

        # =================================
        # GROUP BY
        # =================================

        layout.addWidget(
            QLabel("Group By")
        )

        self.groupby_layout = QVBoxLayout()

        layout.addLayout(
            self.groupby_layout
        )

        self.add_group_button = QPushButton(
            "+ Add Group"
        )

        layout.addWidget(
            self.add_group_button
        )

        self.add_group_button.clicked.connect(
            self.create_groupby_row
        )

        # =================================
        # AGGREGATIONS
        # =================================

        layout.addWidget(
            QLabel("Aggregations")
        )

        self.aggregation_layout = QVBoxLayout()

        layout.addLayout(
            self.aggregation_layout
        )

        self.add_aggregation_button = QPushButton(
            "+ Add Aggregation"
        )

        layout.addWidget(
            self.add_aggregation_button
        )

        self.add_aggregation_button.clicked.connect(
            self.create_aggregation_row
        )

        # =================================
        # APPLY
        # =================================

        self.apply_button = QPushButton(
            "Apply"
        )

        layout.addWidget(
            self.apply_button
        )

        self.apply_button.clicked.connect(
            self.accept
        )

        self.setLayout(layout)

        # Create initial rows
        self.create_groupby_row()
        self.create_aggregation_row()

    # =====================================
    # GROUP BY
    # =====================================

    def create_groupby_row(self):

        row = GroupbyRow(
            self.dataframe
        )

        row.remove_requested.connect(
            self.remove_groupby_row
        )

        self.groupby_layout.addWidget(row)

        self.groupby_rows.append(row)

    def remove_groupby_row(self, row):

        if len(self.groupby_rows) <= 1:
            return

        self.groupby_rows.remove(row)

        self.groupby_layout.removeWidget(row)

        row.deleteLater()

    # =====================================
    # AGGREGATION
    # =====================================

    def create_aggregation_row(self):

        row = AggregationRow(
            self.dataframe
        )

        row.remove_requested.connect(
            self.remove_aggregation_row
        )

        self.aggregation_layout.addWidget(row)

        self.aggregation_rows.append(row)

    def remove_aggregation_row(self, row):

        if len(self.aggregation_rows) <= 1:
            return

        self.aggregation_rows.remove(row)

        self.aggregation_layout.removeWidget(row)

        row.deleteLater()

    # =====================================
    # GET RESULT
    # =====================================

    def get_aggregation(self):

        group_by = [
            row.get_column()
            for row in self.groupby_rows
        ]

        aggregations = [
            row.get_aggregation()
            for row in self.aggregation_rows
        ]

        return Aggregation(
            group_by,
            aggregations
        )