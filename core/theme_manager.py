from qt_material import apply_stylesheet
from PySide6.QtGui import QFont


class ThemeManager:

    def __init__(self, application):

        self.application = application

    def apply_theme(self, settings):

        apply_stylesheet(
            self.application,
            theme=settings.theme
        )

        font = QFont(
            "Segoe UI",
            settings.font_size
        )

        self.application.setFont(font)