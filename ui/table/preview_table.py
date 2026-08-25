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
