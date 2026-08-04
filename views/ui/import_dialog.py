from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QRadioButton,
    QButtonGroup
)


class ImportOptions:
    """Stores the user's import choices."""

    def __init__(self):
        self.header = "infer"
        self.manual_headers = None
        self.header_file = None



class ImportDialog(QDialog):
    """Dialog for selecting CSV import options."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Import CSV")
        self.setMinimumWidth(350)

        self.options = ImportOptions()

        self.build_ui()


    def build_ui(self):

        layout = QVBoxLayout()

        self.button_group = QButtonGroup(self)

        self.auto_button = QRadioButton("Detect automatically")
        self.header_button = QRadioButton("First row contains headers")
        self.no_header_button = QRadioButton("No headers")
        self.manual_button = QRadioButton("Enter headers manually")
        self.file_button = QRadioButton("Load headers from text file")

        self.auto_button.setChecked(True)

        for button in (
            self.auto_button,
            self.header_button,
            self.no_header_button,
            self.manual_button,
            self.file_button,
        ):
            self.button_group.addButton(button)
            layout.addWidget(button)

        buttons = QHBoxLayout()

        import_button = QPushButton("Import")
        cancel_button = QPushButton("Cancel")

        import_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        buttons.addWidget(import_button)
        buttons.addWidget(cancel_button)

        layout.addLayout(buttons)

        self.setLayout(layout)


    def get_options(self):

        if self.auto_button.isChecked():
            self.options.header = "infer"

        elif self.header_button.isChecked():
            self.options.header = 0

        elif self.no_header_button.isChecked():
            self.options.header = None

        elif self.manual_button.isChecked():
            self.options.header = None
            # Manual headers will come later

        elif self.file_button.isChecked():
            self.options.header = None
            # Header file support later

        return self.options