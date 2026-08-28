import sys

from PySide6.QtWidgets import QLabel, QTabWidget, QWidget
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtGui import QIcon
from analysis.data_summary import DataSummary
from PySide6.QtGui import QFont

class StatisticsWidget(QWidget):
    '''Widegt responsible for displaying EDA'''
    def __init__(self):
        super().__init__()

        self.summary = DataSummary()

        layout = QVBoxLayout()

        self.tabs = QTabWidget()

        layout.addWidget(self.tabs)

        self.setLayout(layout)

        self.build_tabs()
        




    def build_tabs(self):


        font = QFont("Consolas")
        font.setPointSize(10)

        self.summary_page = QTextEdit()
        self.summary_page.setReadOnly(True)

        self.columns_page = QTextEdit()
        self.columns_page.setReadOnly(True)

        self.missing_page = QTextEdit()
        self.missing_page.setReadOnly(True)

        self.numeric_page = QTextEdit()
        self.numeric_page.setReadOnly(True)

        self.correlation_page = QTextEdit()
        self.correlation_page.setReadOnly(True)

        self.categorical_page = QTextEdit()
        self.categorical_page.setReadOnly(True)

        self.datetime_page = QTextEdit()
        self.datetime_page.setReadOnly(True)

        self.categorical_page.setFont(font)
        self.datetime_page.setFont(font)


        self.summary_page.setFont(font)
        self.columns_page.setFont(font)
        self.missing_page.setFont(font)
        self.numeric_page.setFont(font)
        self.correlation_page.setFont(font)


        self.tabs.addTab(self.summary_page, "Summary")
        self.tabs.addTab(self.columns_page, "Columns")
        self.tabs.addTab(self.missing_page, "Missing")
        self.tabs.addTab(self.numeric_page, "Numeric")
        self.tabs.addTab(self.categorical_page, "Categorical"        )
        self.tabs.addTab(self.datetime_page, "Date / Time" )
        self.tabs.addTab(self.correlation_page, "Correlation")
        

    def update_statistics(self, dataframe):
        """Refresh statistics for the supplied DataFrame."""

        self.load_dataframe(dataframe)

    def load_dataframe(self, dataframe):

        if dataframe is None:
            self.clear()
            return

        summary = self.summary.generate(
            dataframe
        )

        self.display_summary(summary)
        self.display_columns(summary)
        self.display_missing(summary)
        self.display_numeric(summary)
        self.display_categorical(summary)
        self.display_datetime(summary)
        self.display_correlation(summary)


    def display_summary(self, summary):

        output = [
            f"Rows:            {summary['rows']:,}",
            f"Columns:         {summary['columns']:,}",
            f"Duplicates:      {summary['duplicates']:,}",
            f"Missing values:  {summary['missing_total']:,}",
            f"Memory:          {summary['memory']:,} bytes",
            "",
            "Column types",
            "------------",
        ]

        dtype_counts = {}

        for dtype in summary["dtypes"].values():

            dtype = str(dtype)

            dtype_counts[dtype] = (
                dtype_counts.get(dtype, 0) + 1
            )

        for dtype, count in dtype_counts.items():

            output.append(
                f"{dtype:20} {count}"
            )

        self.summary_page.setPlainText(
            "\n".join(output)
        )
        
    def display_columns(self, summary):

        output = []

        for column, dtype in summary["dtypes"].items():

            output.append(
                f"{str(column):20} {dtype}"
            )

        self.columns_page.setPlainText(
            "\n".join(output)
        )

    def display_missing(self, summary):

        output = []

        rows = summary["rows"]

        for column, count in summary["missing"].items():

            percentage = (
                (count / rows) * 100
                if rows
                else 0
            )

            output.append(
                f"{str(column):20} "
                f"{count:8} "
                f"{percentage:7.2f}%"
            )
        
        self.missing_page.setPlainText(
            "\n".join(output)
        )

    def display_numeric(self, summary):

        numeric = summary["numeric"]

        if numeric is None:

            self.numeric_page.setPlainText(
                "No numeric columns."
            )

        else:

            self.numeric_page.setPlainText(
                numeric.to_string()
            )

    def display_correlation(self, summary):

        correlation = summary["correlations"]

        if correlation is None:

            self.correlation_page.setPlainText(
                "Need at least two numeric columns."
            )

        else:

            self.correlation_page.setPlainText(
                correlation.to_string()
            )

    def clear(self):
        """Clear all displayed statistics."""

        self.summary_page.clear()
        self.columns_page.clear()
        self.missing_page.clear()
        self.numeric_page.clear()
        self.correlation_page.clear()

        self.categorical_page.clear()
        self.datetime_page.clear()

    def display_categorical(self, summary):

        output = []

        for column, info in summary["column_summary"].items():

            dtype = info["dtype"]

            if (
                "object" not in dtype
                and "string" not in dtype
                and "category" not in dtype
            ):
                continue

            output.append(
                f"{column}"
            )
            output.append(
                "-" * len(str(column))
            )
            output.append(
                f"Type:           {dtype}"
            )
            output.append(
                f"Unique:         {info['unique']}"
            )
            output.append(
                f"Missing:        {info['missing']}"
            )
            output.append(
                f"Most common:    {info['mode']}"
            )
            output.append(
                f"Frequency:      {info['mode_frequency']}"
            )
            output.append("")

        self.categorical_page.setPlainText(
            "\n".join(output)
            if output
            else "No categorical columns."
        )

    def display_datetime(self, summary):

        output = []

        for column, info in summary["column_summary"].items():

            dtype = info["dtype"]

            if "datetime" not in dtype:
                continue

            output.append(
                f"{column}"
            )
            output.append(
                "-" * len(str(column))
            )
            output.append(
                f"Type:           {dtype}"
            )
            output.append(
                f"Unique:         {info['unique']}"
            )
            output.append(
                f"Missing:        {info['missing']}"
            )
            output.append(
                f"Minimum:        {info['min']}"
            )
            output.append(
                f"Maximum:        {info['max']}"
            )
            output.append(
                f"Range:          {info['range']}"
            )
            output.append("")

        self.datetime_page.setPlainText(
            "\n".join(output)
            if output
            else "No datetime columns."
        )