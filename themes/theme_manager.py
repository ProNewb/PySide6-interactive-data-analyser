from themes.dark import DARK_THEME
from themes.light import LIGHT_THEME
from PySide6.QtWidgets import QApplication
class ThemeManager:

    @staticmethod
    def apply(theme):
        app = QApplication.instance()

        if theme == "dark":
            app.setStyleSheet(DARK_THEME)
        else:
            app.setStyleSheet(LIGHT_THEME)