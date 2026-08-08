from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView


class GraphWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.browser = QWebEngineView()

        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        self.setLayout(layout)


    def display_graph(self, figure):

        html = figure.to_html(
            include_plotlyjs="cdn"
        )

        self.browser.setHtml(html)