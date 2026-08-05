from PySide6.QtWidgets import QMessageBox, QStatusBar

from views.ui.statistics_widget import StatisticsWidget

from PySide6.QtWidgets import QMessageBox
from views.ui.statistics_widget import StatisticsWidget


class AnalysisController:

    def __init__(self, dataset_manager, table):

        self.dataset_manager = dataset_manager
        self.table = table
        self.stats_widget = StatisticsWidget()


    def show_statistics(self, parent=None):

        dataframe = self.table.get_analysis_dataframe()

        if dataframe is None:

            QMessageBox.warning(
                parent,
                "No Selection",
                "Select data first."
            )

            return


        self.stats_widget.load_dataframe(
            dataframe
        )

        self.stats_widget.show()