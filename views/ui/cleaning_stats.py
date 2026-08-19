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
        self.current_label = QLabel()
        self.result_label = QLabel()

        layout.addWidget(self.rows_label)
        layout.addWidget(self.columns_label)
        layout.addWidget(self.current_label)
        layout.addWidget(self.result_label)

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

        self.current_label.setText(
            f"Current: {summary['missing_total']} missing, "
            f"{summary['duplicates']} duplicates"
        )

        self.result_label.setText("Result: -")

    def update_missing(self, dataframe, columns=None):
        """Display missing-value statistics for selected columns."""

        if dataframe is None:
            self.clear()
            return

        summary = self.summary.generate(dataframe)

        if columns is None:
            columns = list(dataframe.columns)

        self.update_comparison(dataframe, None, columns, "missing")

    def update_duplicates(self, dataframe, columns=None):
        """Display duplicate statistics for selected columns."""

        if dataframe is None:
            self.clear()
            return

        self.update_comparison(dataframe, None, columns, "duplicates")

    def update_comparison(self, current, result, columns, operation):
        """Show before/after stats for the selected columns."""
        if current is None:
            self.clear()
            return

        selected = list(columns or current.columns)
        result_frame = result if result is not None else current

        if operation == "duplicates":
            current_value = int(current.duplicated(subset=selected).sum())
            result_value = int(result_frame.duplicated(subset=selected).sum())
            label = "duplicates"
        else:
            current_value = int(current[selected].isna().sum().sum())
            result_value = int(result_frame[selected].isna().sum().sum())
            label = "missing values"

        self.rows_label.setText(
            f"Rows: {len(current)} -> {len(result_frame)}"
        )
        self.columns_label.setText(
            f"Selected columns: {len(selected)}"
        )
        self.current_label.setText(
            f"Current {label}: {current_value}"
        )
        self.result_label.setText(
            f"Result {label}: {result_value}"
            if result is not None
            else f"Result {label}: -"
        )

    def clear(self):
        """Reset all displayed statistics."""

        self.rows_label.setText("Rows: -")
        self.columns_label.setText("Columns: -")
        self.current_label.setText("Current: -")
        self.result_label.setText("Result: -")