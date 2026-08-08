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


from core.graph_generator import GraphGenerator
from views.ui.graph_widget import GraphWidget

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QLineEdit,
    QSpinBox
)


from core.graph_generator import GraphGenerator
from views.ui.graph_widget import GraphWidget

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QLineEdit,
    QSpinBox
)


class GraphTab(QWidget):

    def __init__(self):
        super().__init__()

        self.dataframe = None

        self.graph_widget = GraphWidget()
        self.generator = GraphGenerator()
        self.color_column = QComboBox()
        # -------------------------
        # Graph type
        # -------------------------

        self.graph_type = QComboBox()

        self.graph_type.addItems([
            "Scatter",
            "Line",
            "Bar",
            "Histogram",
            "Box",
            "Pie",
            "Donut",
            "Area",
            "Bubble",
            "3D Scatter",
            "Map",
            "Tree Map"
        ])

        # -------------------------
        # Column selectors
        # -------------------------

        self.x_column = QComboBox()
        self.y_column = QComboBox()
        self.z_column = QComboBox()
        self.size_column = QComboBox()

        # -------------------------
        # Histogram bins
        # -------------------------

        self.bins_input = QSpinBox()
        self.bins_input.setMinimum(1)
        self.bins_input.setMaximum(500)
        self.bins_input.setValue(20)

        # -------------------------
        # Title
        # -------------------------

        self.title_input = QLineEdit()

        self.title_input.setPlaceholderText(
            "Graph title"
        )

        # -------------------------
        # Generate button
        # -------------------------

        self.generate_button = QPushButton(
            "Generate Graph"
        )

        self.build_ui()

        # -------------------------
        # Signals
        # -------------------------

        self.generate_button.clicked.connect(
            self.generate_graph
        )

        self.graph_type.currentTextChanged.connect(
            self.update_controls
        )

        # Set initial visibility
        self.update_controls(
            self.graph_type.currentText()
        )

    # ==================================================
    # UI
    # ==================================================

    def build_ui(self):

        main_layout = QHBoxLayout()

        controls = QVBoxLayout()
        self.color_label = QLabel("Colour")

        controls.addWidget(
            self.color_label
        )

        controls.addWidget(
            self.color_column
        )
        # -------------------------
        # Graph type
        # -------------------------

        controls.addWidget(
            QLabel("Graph Type")
        )

        controls.addWidget(
            self.graph_type
        )

        # -------------------------
        # X
        # -------------------------

        self.x_label = QLabel("X Axis")

        controls.addWidget(
            self.x_label
        )

        controls.addWidget(
            self.x_column
        )

        # -------------------------
        # Y
        # -------------------------

        self.y_label = QLabel("Y Axis")

        controls.addWidget(
            self.y_label
        )

        controls.addWidget(
            self.y_column
        )

        # -------------------------
        # Z
        # -------------------------

        self.z_label = QLabel("Z Axis")

        controls.addWidget(
            self.z_label
        )

        controls.addWidget(
            self.z_column
        )

        # -------------------------
        # Size
        # -------------------------

        self.size_label = QLabel("Bubble Size")

        controls.addWidget(
            self.size_label
        )

        controls.addWidget(
            self.size_column
        )

        # -------------------------
        # Bins
        # -------------------------

        self.bins_label = QLabel("Number of Bins")

        controls.addWidget(
            self.bins_label
        )

        controls.addWidget(
            self.bins_input
        )
        

        # -------------------------
        # Title
        # -------------------------

        controls.addWidget(
            QLabel("Title")
        )

        controls.addWidget(
            self.title_input
        )

        # -------------------------
        # Generate
        # -------------------------

        controls.addWidget(
            self.generate_button
        )

        controls.addStretch()

        # -------------------------
        # Main layout
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

    # ==================================================
    # Control visibility
    # ==================================================

    def update_controls(self, graph_type):

        # Start by hiding everything
        self.x_label.setVisible(False)
        self.x_column.setVisible(False)

        self.y_label.setVisible(False)
        self.y_column.setVisible(False)

        self.z_label.setVisible(False)
        self.z_column.setVisible(False)

        self.size_label.setVisible(False)
        self.size_column.setVisible(False)

        self.bins_label.setVisible(False)
        self.bins_input.setVisible(False)
        self.color_label.setVisible(False)
        self.color_column.setVisible(False)
        # ----------------------------------------------
        # X + Y graphs
        # ----------------------------------------------

        if graph_type in [
            "Scatter",
            "Line",
            "Bar",
            "Box",
            "Area"
        ]:

            self.x_label.setVisible(True)
            self.x_column.setVisible(True)

            self.y_label.setVisible(True)
            self.y_column.setVisible(True)

        # ----------------------------------------------
        # Histogram
        # ----------------------------------------------

        elif graph_type == "Histogram":

            self.x_label.setText(
                "Column"
            )

            self.x_label.setVisible(True)
            self.x_column.setVisible(True)

            self.bins_label.setVisible(True)
            self.bins_input.setVisible(True)

        # ----------------------------------------------
        # Pie / Donut
        # ----------------------------------------------

        elif graph_type in [
            "Pie",
            "Donut"
        ]:

            self.x_label.setText(
                "Category"
            )

            self.y_label.setText(
                "Value"
            )

            self.x_label.setVisible(True)
            self.x_column.setVisible(True)

            self.y_label.setVisible(True)
            self.y_column.setVisible(True)

        # ----------------------------------------------
        # Bubble
        # ----------------------------------------------

        elif graph_type == "Bubble":

            self.x_label.setText(
                "X Axis"
            )

            self.y_label.setText(
                "Y Axis"
            )

            self.x_label.setVisible(True)
            self.x_column.setVisible(True)

            self.y_label.setVisible(True)
            self.y_column.setVisible(True)

            self.size_label.setVisible(True)
            self.size_column.setVisible(True)

        # ----------------------------------------------
        # 3D Scatter
        # ----------------------------------------------

        elif graph_type == "3D Scatter":

            self.x_label.setText(
                "X Axis"
            )

            self.y_label.setText(
                "Y Axis"
            )

            self.z_label.setText(
                "Z Axis"
            )

            self.x_label.setVisible(True)
            self.x_column.setVisible(True)

            self.y_label.setVisible(True)
            self.y_column.setVisible(True)

            self.z_label.setVisible(True)
            self.z_column.setVisible(True)

        # ----------------------------------------------
        # Map
        # ----------------------------------------------

        elif graph_type == "Map":

            self.x_label.setText(
                "Longitude"
            )

            self.y_label.setText(
                "Latitude"
            )

            self.x_label.setVisible(True)
            self.x_column.setVisible(True)

            self.y_label.setVisible(True)
            self.y_column.setVisible(True)

        # ----------------------------------------------
        # Tree Map
        # ----------------------------------------------

        elif graph_type == "Tree Map":

            self.x_label.setText(
                "Category"
            )

            self.y_label.setText(
                "Value"
            )

            self.x_label.setVisible(True)
            self.x_column.setVisible(True)

            self.y_label.setVisible(True)
            self.y_column.setVisible(True)

        elif graph_type in [
                "Scatter",
                "Line",
                "Bar",
                "Box",
                "Area",
                "Bubble",
                "3D Scatter"
            ]:

                self.color_label.setVisible(True)
                self.color_column.setVisible(True)
    # ==================================================
    # DataFrame
    # ==================================================

    def set_dataframe(self, dataframe):

        self.dataframe = dataframe.copy()

        self.x_column.clear()
        self.y_column.clear()
        self.z_column.clear()
        self.size_column.clear()
        self.color_column.clear()


        self.color_column.addItem(
            "None",
            userData=None
        )

        for column in dataframe.columns:

            column_name = str(column)
            self.x_column.addItem(column_name, userData=column)
            self.y_column.addItem(column_name, userData=column)
            self.z_column.addItem(column_name, userData=column)
            self.size_column.addItem(column_name, userData=column)
            self.color_column.addItem(column_name, userData=column)
           

            # ==================================================
    # Generate graph
    # ==================================================

    def generate_graph(self):

        if self.dataframe is None:
            return

        graph_type = self.graph_type.currentText()

        title = self.title_input.text()

        x = self.x_column.currentData()
        y = self.y_column.currentData()
        z = self.z_column.currentData()
        size = self.size_column.currentData()
        color = self.color_column.currentData()
        bins = self.bins_input.value()

        # ----------------------------------------------
        # Histogram
        # ----------------------------------------------

        if graph_type == "Histogram":

            figure = self.generator.create_graph(
                self.dataframe,
                graph_type,
                x_column=x,
                bins=bins,
                title=title
            )

        # ----------------------------------------------
        # 3D Scatter
        # ----------------------------------------------

        elif graph_type == "3D Scatter":

            figure = self.generator.create_graph(
                self.dataframe,
                graph_type,
                x_column=x,
                y_column=y,
                z_column=z,
                title=title
            )

        # ----------------------------------------------
        # Bubble
        # ----------------------------------------------

        elif graph_type == "Bubble":

            figure = self.generator.create_graph(
                self.dataframe,
                graph_type,
                x_column=x,
                y_column=y,
                z_column=size,
                title=title
            )

        # ----------------------------------------------
        # All other graphs
        # ----------------------------------------------

        else:

            figure = self.generator.create_graph(
                self.dataframe,
                graph_type,
                x_column=x,
                y_column=y,
                title=title
            )

        self.graph_widget.display_graph(
            figure
        )