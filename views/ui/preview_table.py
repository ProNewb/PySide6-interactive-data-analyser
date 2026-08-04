from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


class PreviewTable(QTableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setEditTriggers(
            QTableWidget.NoEditTriggers
        )


    def display_dataframe(self, df):

        preview = df.head(10)

        self.setRowCount(
            len(preview)
        )

        self.setColumnCount(
            len(preview.columns)
        )

        self.setHorizontalHeaderLabels(
            [
                str(col)
                for col in preview.columns
            ]
        )

        for row in range(len(preview)):

            for col in range(len(preview.columns)):

                self.setItem(
                    row,
                    col,
                    QTableWidgetItem(
                        str(preview.iat[row,col])
                    )
                )