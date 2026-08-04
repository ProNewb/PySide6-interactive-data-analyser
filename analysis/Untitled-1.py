


from analysis.data_summary import DataSummary


class summary_widget:
    def __init__(self, df):
        self.summary = DataSummary().generate(df)
        self.rows_label.setText(
    str(self.summary["rows"])
)

