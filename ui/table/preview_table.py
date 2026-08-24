from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from core.dataset_table import DataTable



class PreviewTable(DataTable):

    def display_dataframe(self, dataframe, full=False):

        if dataframe is None:
            super().display_dataframe(None)
            return

        if not full:
            dataframe = dataframe.head(10)

        super().display_dataframe(dataframe)

        self.setEditTriggers(
            QTableWidget.NoEditTriggers
        )


    def old_display_dataframe(self, df, rows=20, full=False):

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