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
        
        self.summary_page.setFont(font)
        self.columns_page.setFont(font)
        self.missing_page.setFont(font)
        self.numeric_page.setFont(font)
        self.correlation_page.setFont(font)
        self.tabs.addTab(self.summary_page, "Summary")
        self.tabs.addTab(self.columns_page, "Columns")
        self.tabs.addTab(self.missing_page, "Missing")
        self.tabs.addTab(self.numeric_page, "Numeric")
        self.tabs.addTab(self.correlation_page, "Correlation")
        

    def update_statistics(self, dataframe):
        
        if dataframe is not None:
            self.load_dataframe(dataframe)
        else:
            self.text.setPlainText("No data loaded.")

    def load_dataframe(self, df):
        if df is not None:
        
            summary = {}

            summary["rows"] = len(df)

            summary["columns"] = len(df.columns)

            summary["column_names"] = list(df.columns)

            summary["dtypes"] = df.dtypes

            summary["missing"] = df.isnull().sum()

            summary["duplicates"] = df.duplicated().sum()

            summary["memory"] = df.memory_usage(deep=True).sum()

            summary["numeric"] = df.describe()


            categorical = df.select_dtypes(
                include=["string", "object"]
            )

            if not categorical.empty:
                summary["categorical"] = categorical.describe()
            else:
                summary["categorical"] = None

            if summary["categorical"] is None:
                self.columns_page.setPlainText(
                    "No categorical columns."
                )
            else:
                self.columns_page.setPlainText(
                    summary["categorical"].to_string()
                )

            #summary["correlations"] = df.corr(numeric_only=True)

            numeric = df.select_dtypes(include="number")

            if len(numeric.columns) >= 2:
                summary["correlations"] = numeric.corr()
            else:
                summary["correlations"] = None

            summary_output = []

            summary_output.append(f"Rows: {summary['rows']}")
            summary_output.append(f"Columns: {summary['columns']}")
            summary_output.append(f"Duplicates: {summary['duplicates']}")
            summary_output.append(f"Memory: {summary['memory']:,} bytes")

            self.summary_page.setPlainText(
                "\n".join(summary_output)
            )


            column_output = []

            for column, dtype in summary["dtypes"].items():
                column_output.append(
                    f"{column:20} {dtype}"
                )

            self.columns_page.setPlainText(
                "\n".join(column_output)
            )

            missing_output = []

            for column, value in summary["missing"].items():
                missing_output.append(
                    f"{column:20} {value}"
                )

            self.missing_page.setPlainText(
                "\n".join(missing_output)
            )

            self.numeric_page.setPlainText(
                summary["numeric"].to_string()
            )

            if summary["correlations"] is None:

                self.correlation_page.setPlainText(
                    "Need at least two numeric columns."
                )

            else:

                self.correlation_page.setPlainText(
                    summary["correlations"].to_string()
                )