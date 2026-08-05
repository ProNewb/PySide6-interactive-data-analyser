from PySide6.QtWidgets import QMessageBox, QStatusBar

from views.ui.statistics_widget import StatisticsWidget

from PySide6.QtWidgets import QMessageBox
from views.ui.statistics_widget import StatisticsWidget


class AnalysisController:

    def __init__(self, dataset_manager):

        self.dataset_manager = dataset_manager
        self.stats_widget = StatisticsWidget()


    def show_statistics(self, parent=None):

        if not self.dataset_manager.has_data():

            QMessageBox.warning(
                parent,
                "No Dataset",
                "Please load a CSV first."
            )

            return

        dataframe = self.dataset_manager.get_dataframe()

        self.stats_widget.load_dataframe(
            dataframe
        )

        self.stats_widget.show()