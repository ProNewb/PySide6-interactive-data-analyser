

from views.ui.__pycache__.graph_widget import GraphWidget
from views.ui.statistics_widget import StatisticsWidget
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout
)


class AnalysisTab(QWidget):

    def __init__(self):

        super().__init__()

        self.statistics = StatisticsWidget()
        self.graphs = GraphWidget()

        layout = QVBoxLayout()

        layout.addWidget(
            self.statistics
        )

        layout.addWidget(
            self.graphs
        )

        self.setLayout(layout)