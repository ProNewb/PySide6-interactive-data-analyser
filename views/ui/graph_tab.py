from core.graph_generator import GraphGenerator
from views.ui.graph_controls import GraphControls
from views.ui.graph_widget import GraphWidget
from PySide6.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QLineEdit
)

from views.ui.graph_widget import GraphWidget


class GraphTab(QWidget):

    def __init__(self):
        super().__init__()

        self.dataframe = None

        self.graph_widget = GraphWidget()
        self.generator = GraphGenerator()

        self.controls = GraphControls()

        self.graph_type = QComboBox()
        self.graph_type.addItems([
            "Scatter",
            "Line",
            "Bar",
            "Histogram"
        ])

        self.x_column = QComboBox()
        self.y_column = QComboBox()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(
            "Graph title"
        )

        self.generate_button = QPushButton(
            "Generate Graph"
        )

        self.build_ui()
        self.generate_button.clicked.connect(
            self.generate_graph
        )
    def build_ui(self):

        main_layout = QHBoxLayout()

        # -------------------------
        # Right-hand controls
        # -------------------------

        controls = QVBoxLayout()

        controls.addWidget(
            QLabel("Graph Type")
        )

        controls.addWidget(
            self.graph_type
        )

        controls.addWidget(
            QLabel("X Axis")
        )

        controls.addWidget(
            self.x_column
        )

        controls.addWidget(
            QLabel("Y Axis")
        )

        controls.addWidget(
            self.y_column
        )

        controls.addWidget(
            QLabel("Title")
        )

        controls.addWidget(
            self.title_input
        )

        controls.addWidget(
            self.generate_button
        )

        controls.addStretch()

        # -------------------------
        # Layout
        # -------------------------

        main_layout.addWidget(
            self.graph_widget,
            1
        )

        main_layout.addLayout(
            controls
        )

        self.setLayout(
            main_layout
        )


    def set_dataframe(self, dataframe):

        self.dataframe = dataframe.copy()

        self.x_column.clear()
        self.y_column.clear()

        for column in dataframe.columns:

            self.x_column.addItem(
                str(column),
                userData=column
            )

            self.y_column.addItem(
                str(column),
                userData=column
            )


    def generate_graph(self):

        if self.dataframe is None:
            return

        graph_type = self.graph_type.currentText()
        x = self.x_column.currentData()
        y = self.y_column.currentData()
        title = self.title_input.text()

        figure = self.generator.create_graph(
            self.dataframe,
            graph_type,
            x,
            y,
            title
        )

        self.graph_widget.display_graph(
            figure
        )