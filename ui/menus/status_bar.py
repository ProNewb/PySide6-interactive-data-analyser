from PySide6.QtWidgets import QStatusBar


class StatusBar(QStatusBar):
    '''statusbar'''
    def __init__(self):
        super().__init__()

        self.showMessage(
            "Ready"
        )