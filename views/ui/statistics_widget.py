from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QVBoxLayout

from analysis.data_summary import DataSummary


class StatisticsWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.summary = DataSummary()

        layout = QVBoxLayout()

        self.text = QTextEdit()
        self.text.setReadOnly(True)

        layout.addWidget(self.text)

        self.setLayout(layout)



    def load_dataframe(self, dataframe):

        summary = self.summary.generate(dataframe)

        output = []

        output.append(f"Rows: {summary['rows']}")
        output.append(f"Columns: {summary['columns']}")
        output.append("")

        output.append("Column Names")

        for column in summary["column_names"]:
            output.append(column)

        output.append("")
        output.append("Missing Values")

        for column, missing in summary["missing"].items():
            output.append(f"{column}: {missing}")

        self.text.setPlainText(
            "\n".join(output)
        )