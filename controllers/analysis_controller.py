from PySide6.QtWidgets import QMessageBox

from views.ui.statistics_widget import StatisticsWidget


class AnalysisController:
    """OBSOLETE Coordinate analysis operations performed on dataset selections."""

    def __init__(self, dataset_manager, table):

        self.dataset_manager = dataset_manager
        self.table = table

        # Widget used when statistics are displayed separately.
        self.stats_widget = StatisticsWidget()

    def show_statistics(self, parent=None):
        """Display statistics for the currently selected data."""

        dataframe = self.table.get_analysis_dataframe()

        if dataframe is None:

            QMessageBox.warning(
                parent,
                "No Data",
                "Please load a dataset first."
            )

            return

        self.stats_widget.load_dataframe(
            dataframe
        )

        self.stats_widget.show()