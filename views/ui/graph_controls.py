from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QCheckBox
)


class GraphControls(QWidget):
    '''GUI class for graphical interface'''
    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        # Graph type
        layout.addWidget(
            QLabel("Graph Type")
        )

        self.graph_type = QComboBox()
        
        self.graph_type.addItems([
            "Scatter",
            "Line",
            "Bar",
            "Histogram"
        ])

        layout.addWidget(
            self.graph_type
        )


        # X axis
        layout.addWidget(
            QLabel("X Axis")
        )

        self.x_column = QComboBox()

        layout.addWidget(
            self.x_column
        )


        # Y axis
        layout.addWidget(
            QLabel("Y Axis")
        )

        self.y_column = QComboBox()

        layout.addWidget(
            self.y_column
        )


        # Title
        layout.addWidget(
            QLabel("Title")
        )

        self.title = QLineEdit()

        self.title.setPlaceholderText(
            "Graph title"
        )

        layout.addWidget(
            self.title
        )


        # Legend
        self.legend = QCheckBox(
            "Show Legend"
        )

        layout.addWidget(
            self.legend
        )


        # Generate
        self.generate_button = QPushButton(
            "Generate Graph"
        )

        layout.addWidget(
            self.generate_button
        )

        layout.addStretch()

        self.setLayout(layout)