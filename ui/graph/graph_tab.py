import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go 
from core.graph_generator import GraphGenerator
from ui.menus.graph_controls import GraphControls
from ui.graph.graph_widget import GraphWidget
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QMessageBox, QSpinBox, QWidget, QVBoxLayout

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QLineEdit
)

from ui.graph.graph_widget import GraphWidget




class GraphTab(QWidget):
    '''Class responsible for the Graph tab on both the main and result dataset'''
    def __init__(self):
        super().__init__()

        #self.dataframe_provider = dataframe_provider
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
            ,"Heatmap"
            ,"Correlation Map"
        ])

        # -------------------------
        # Column selectors
        # -------------------------

        self.x_column = QComboBox()
        self.y_column = QComboBox()
        self.z_column = QComboBox()
        self.size_column = QComboBox()
        self.group_check = QCheckBox("Group categories")
        self.group_column = QComboBox()
        self.group_aggregation = QComboBox()
        self.group_aggregation.addItem("Average", "mean")
        self.group_aggregation.addItem("Sum", "sum")
        self.group_aggregation.addItem("Count", "count")
        self.group_limit = QSpinBox()
        self.group_limit.setRange(2, 1000)
        self.group_limit.setValue(20)

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
        self.trendline_check = QCheckBox("Show trend line / curve")
        self.bell_curve_check = QCheckBox("Show bell curve")

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
        self.group_check.toggled.connect(self.update_group_controls)
        '''self.group_column.currentIndexChanged.connect(self.generate_graph)
        self.group_aggregation.currentIndexChanged.connect(self.generate_graph)
        self.group_limit.valueChanged.connect(self.generate_graph)'''

        # Set initial visibility
        self.update_controls(
            self.graph_type.currentText()
        )
        self.update_group_controls()

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

        controls.addWidget(self.group_check)
        controls.addWidget(QLabel("Group column"))
        controls.addWidget(self.group_column)
        controls.addWidget(QLabel("Group aggregation"))
        controls.addWidget(self.group_aggregation)
        controls.addWidget(QLabel("Keep top groups"))
        controls.addWidget(self.group_limit)
        

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

        controls.addWidget(self.trendline_check)
        controls.addWidget(self.bell_curve_check)

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
        self.group_check.setVisible(False)
        self.group_column.setVisible(False)
        self.group_aggregation.setVisible(False)
        self.group_limit.setVisible(False)
        self.color_label.setVisible(False)
        self.color_column.setVisible(False)
        self.trendline_check.setVisible(False)
        self.bell_curve_check.setVisible(False)
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
            self.trendline_check.setVisible(
                graph_type in {"Scatter", "Line", "Area", "Bubble"}
            )
            self.group_check.setVisible(True)
            self.trendline_check.setVisible(
                graph_type in {"Scatter", "Line", "Area", "Bubble"}
            )

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
            self.bell_curve_check.setVisible(True)

        elif graph_type in {"Heatmap", "Correlation Map"}:
            self.trendline_check.setVisible(False)

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
            self.trendline_check.setVisible(True)

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

        self.update_group_controls()

    def update_group_controls(self):

        enabled = (
            self.group_check.isChecked()
            and self.group_check.isVisible()
        )

        self.group_column.setEnabled(enabled)
        self.group_aggregation.setEnabled(enabled)

        if not enabled:
            return

        group = self.group_column.currentData()

        current = self.y_column.currentData()

        self.y_column.blockSignals(True)
        self.y_column.clear()

        for col in self.dataframe.columns:
            if col != group:
                self.y_column.addItem(str(col), col)

        if current != group:
            index = self.y_column.findData(current)
            if index >= 0:
                self.y_column.setCurrentIndex(index)

        self.y_column.blockSignals(False)

    def grouped_dataframe(self):
        if not self.group_check.isVisible() or not self.group_check.isChecked():
            return self.dataframe, self.x_column.currentData(), self.y_column.currentData()
        group_column = self.group_column.currentData()
        value_column = self.y_column.currentData()
        if group_column == value_column:
            raise ValueError(
                "Group column and value column must be different."
            )
        if group_column is None or value_column is None:
            return self.dataframe, self.x_column.currentData(), value_column
        grouped = (
            self.dataframe.groupby(group_column, dropna=False)[value_column]
            .agg(self.group_aggregation.currentData())
            .nlargest(self.group_limit.value())
            .reset_index()
        )
        return grouped, group_column, value_column

    def valid_column(self, dataframe, column):
        return column in dataframe.columns if column is not None else False
    # ==================================================
    # DataFrame
    # ==================================================

    def set_dataframe(self, dataframe):

        # ----------------------------------
        # Clear existing data
        # ----------------------------------

        if dataframe is None:
            self.dataframe = None

            self.x_column.clear()
            self.y_column.clear()
            self.z_column.clear()
            self.size_column.clear()
            self.color_column.clear()
            self.group_column.clear()

            return

        self.dataframe = dataframe.copy()

        # ----------------------------------
        # Prevent signals firing while
        # rebuilding the controls
        # ----------------------------------

        widgets = [
            self.x_column,
            self.y_column,
            self.z_column,
            self.size_column,
            self.color_column,
            self.group_column
        ]

        for widget in widgets:
            widget.blockSignals(True)

        try:

            self.x_column.clear()
            self.y_column.clear()
            self.z_column.clear()
            self.size_column.clear()
            self.color_column.clear()
            self.group_column.clear()

            self.color_column.addItem(
                "None",
                userData=None
            )

            for column in dataframe.columns:

                column_name = str(column)

                self.x_column.addItem(
                    column_name,
                    userData=column
                )

                self.y_column.addItem(
                    column_name,
                    userData=column
                )

                self.z_column.addItem(
                    column_name,
                    userData=column
                )

                self.size_column.addItem(
                    column_name,
                    userData=column
                )

                self.color_column.addItem(
                    column_name,
                    userData=column
                )

                self.group_column.addItem(
                    column_name,
                    userData=column
                )

        finally:

            for widget in widgets:
                widget.blockSignals(False)

        self.update_group_controls()

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
        graph_dataframe, grouped_x, grouped_y = self.grouped_dataframe()
        if graph_type not in {"Histogram", "Heatmap", "Correlation Map"}:

            if x is None or x not in graph_dataframe.columns:
                return

            if y is None or y not in graph_dataframe.columns:
                return
        if graph_type == "3D Scatter":
            graph_dataframe = self.dataframe

        if not all(
            self.valid_column(graph_dataframe, column)
            for column in (x, y, z)
            if column is not None
        ):
            QMessageBox.warning(
                self,
                "Graph error",
                "One or more selected columns are unavailable for this chart."
            )
            return

        # ----------------------------------------------
        # Histogram
        # ----------------------------------------------

        if graph_type == "Histogram":

            figure = self.generator.create_graph(
                graph_dataframe,
                graph_type,
                x_column=x,
                bins=bins,
                title=title,
                bell_curve=self.bell_curve_check.isChecked()
            )

        elif graph_type in {"Heatmap", "Correlation Map"}:
            figure = self.generator.create_graph(
                graph_dataframe,
                graph_type,
                title=title
            )

        # ----------------------------------------------
        # 3D Scatter
        # ----------------------------------------------

        elif graph_type == "3D Scatter":

            figure = self.generator.create_graph(
                graph_dataframe,
                graph_type,
                x_column=x,
                y_column=y,
                z_column=z,
                title=title,
                trendline=self.trendline_check.isChecked()
            )

        # ----------------------------------------------
        # Bubble
        # ----------------------------------------------

        elif graph_type == "Bubble":

            figure = self.generator.create_graph(
                graph_dataframe,
                graph_type,
                x_column=x,
                y_column=y,
                z_column=size,
                title=title,
                trendline=self.trendline_check.isChecked()
            )

        # ----------------------------------------------
        # All other graphs
        # ----------------------------------------------

        else:

            figure = self.generator.create_graph(
                graph_dataframe,
                graph_type,
                x_column=x,
                y_column=y,
                title=title,
                trendline=self.trendline_check.isChecked()
            )

        try:
            self.graph_widget.display_graph(figure)
        except (ValueError, TypeError, KeyError) as error:
            QMessageBox.warning(
                self,
                "Graph error",
                str(error)
            )


    def current_dataframe(self):

        return self.dataframe_provider()