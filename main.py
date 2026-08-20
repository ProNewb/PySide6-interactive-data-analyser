import sys

from PySide6.QtWidgets import QApplication

from core.settings_manager import SettingsManager
from core.theme_manager import ThemeManager
from views.ui.main_window import MainWindow


def main():

    app = QApplication(sys.argv)

    settings_manager = SettingsManager()

    theme_manager = ThemeManager(app)

    theme_manager.apply_theme(
        settings_manager.settings
    )

    window = MainWindow(
        settings_manager,
        theme_manager
    )

    if settings_manager.settings.start_maximized:
        window.showMaximized()
    else:
        window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()