from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


class PreviewTable(QTableWidget):
    '''Preview tables show 20 rows unless a caller explicitly requests all.'''
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setEditTriggers(
            QTableWidget.NoEditTriggers
        )


    def display_dataframe(self, df, rows=20, full=False):

        preview = df if full else df.head(rows)

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