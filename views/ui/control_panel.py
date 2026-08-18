from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout
)


class ControlPanel(QWidget):
    '''***Main controls - old ***'''
    def __init__(self):
        super().__init__()
        ## side menu 
        layout = QVBoxLayout()

        self.load_button = QPushButton("Load CSV")
        self.display_data_button = QPushButton("Display Data")
        self.stats_button = QPushButton("Statistics")
        self.graph_button = QPushButton("Graphs")

        layout.addWidget(self.load_button)
        layout.addWidget(self.display_data_button)
        layout.addWidget(self.stats_button)
        layout.addWidget(self.graph_button)

        layout.addStretch()

        self.setLayout(layout)