import sys

from PySide6.QtWidgets import QApplication

from views.ui.main_window import MainWindow


def main():
    """Start the Data Explorer application."""

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":

    


    main()