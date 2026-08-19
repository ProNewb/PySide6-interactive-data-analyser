from PySide6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QWidget
)

from analysis.data_summary import DataSummary


class CleaningStats(QWidget):
    """Display statistics relevant to the current cleaning operation."""

    def __init__(self):

        super().__init__()

        self.summary = DataSummary()

        layout = QVBoxLayout(self)

        self.rows_label = QLabel()
        self.columns_label = QLabel()
        self.missing_label = QLabel()
        self.duplicate_label = QLabel()

        layout.addWidget(self.rows_label)
        layout.addWidget(self.columns_label)
        layout.addWidget(self.missing_label)
        layout.addWidget(self.duplicate_label)

        self.clear()

    def update(self, dataframe):
        """Update cleaning statistics for the supplied DataFrame."""

        if dataframe is None:
            self.clear()
            return

        summary = self.summary.generate(dataframe)

        self.rows_label.setText(
            f"Rows: {summary['rows']}"
        )

        self.columns_label.setText(
            f"Columns: {summary['columns']}"
        )

        self.missing_label.setText(
            f"Missing values: {summary['missing_total']}"
        )

        self.duplicate_label.setText(
            f"Duplicate rows: {summary['duplicates']}"
        )

    def update_missing(self, dataframe, columns=None):
        """Display missing-value statistics for selected columns."""

        if dataframe is None:
            self.clear()
            return

        summary = self.summary.generate(dataframe)

        if columns is None:
            columns = list(dataframe.columns)

        missing = sum(
            summary["missing"].get(column, 0)
            for column in columns
        )

        self.rows_label.setText(
            f"Rows: {summary['rows']}"
        )

        self.columns_label.setText(
            f"Columns selected: {len(columns)}"
        )

        self.missing_label.setText(
            f"Missing values in selection: {missing}"
        )

        self.duplicate_label.setText(
            f"Duplicate rows: {summary['duplicates']}"
        )

    def update_duplicates(self, dataframe, columns=None):
        """Display duplicate statistics for selected columns."""

        if dataframe is None:
            self.clear()
            return

        if columns:
            duplicate_count = dataframe.duplicated(
                subset=columns
            ).sum()
        else:
            duplicate_count = dataframe.duplicated().sum()

        self.rows_label.setText(
            f"Rows: {len(dataframe)}"
        )

        self.columns_label.setText(
            f"Columns selected: {len(columns or dataframe.columns)}"
        )

        self.missing_label.setText(
            f"Missing values: {dataframe.isna().sum().sum()}"
        )

        self.duplicate_label.setText(
            f"Duplicates: {duplicate_count}"
        )

    def clear(self):
        """Reset all displayed statistics."""

        self.rows_label.setText("Rows: -")
        self.columns_label.setText("Columns: -")
        self.missing_label.setText("Missing values: -")
        self.duplicate_label.setText("Duplicates: -")