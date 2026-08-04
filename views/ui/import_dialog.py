from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QWidget,
    QComboBox,
)
from core.header_reader import HeaderReader
from views.ui.preview_table import PreviewTable
from core.csv_reader import CSVReader


class ImportOptions:

    def __init__(self):

        # Header options
        self.header = 0
        self.manual_headers = None
        self.header_file = None

        # CSV formatting
        self.delimiter = ","

        # Data handling
        self.infer_types = True



class ImportDialog(QDialog):
    """Dialog for selecting CSV import options."""

    def __init__(self, filename, parent=None):
        super().__init__(parent)

        self.filename = filename

        self.reader = CSVReader()
        self.preview_table = PreviewTable()

        self.options = ImportOptions()


        self.build_ui()

        self.manual_inputs = []
        df = self.reader.read(
            self.filename,
            self.options,
            preview=True
        )
        self.num_columns = len(df.columns)
        self.update_preview()

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


## header

        self.header_file_button = QPushButton("Browse Header File...")
        self.header_file_button.setEnabled(False)
        #self.update_preview()
        layout.addWidget(self.header_file_button)

        self.header_file_button.clicked.connect(
        self.select_header_file
    )
                            ## delim

        self.delimiter_box = QComboBox()

        self.delimiter_box.addItems(
            [
                ",",
                ";",
                "\t",
                "|"
            ]
        )

        layout.addWidget(
            QLabel("Delimiter")
        )

        layout.addWidget(
            self.delimiter_box
        )


        layout.addWidget(




                ## preview
        QLabel("Preview")
        )

        layout.addWidget(
            self.preview_table
        )

                # Scroll area for manual header inputs
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.manual_widget = QWidget()
        self.manual_layout = QVBoxLayout(self.manual_widget)
        self.scroll_area.setWidget(self.manual_widget)
        self.scroll_area.setVisible(False)  # Hidden until manual selected
        layout.addWidget(self.scroll_area)

        # Connect manual button to show inputs
        self.manual_button.toggled.connect(self.show_manual_inputs)

        # Buttons
        buttons = QHBoxLayout()
        import_button = QPushButton("Import")
        cancel_button = QPushButton("Cancel")

        import_button.clicked.connect(self.on_import)
        cancel_button.clicked.connect(self.reject)

        buttons.addWidget(import_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)
        self.setLayout(layout)

        self.auto_button.toggled.connect(
        self.update_preview
    )

        self.header_button.toggled.connect(
            self.update_preview
        )

        self.no_header_button.toggled.connect(
            self.update_preview
        )

        self.file_button.toggled.connect(
            self.header_file_button.setEnabled
        )

        self.file_button.toggled.connect(
            self.update_preview
        )
    def show_manual_inputs(self, checked):

        if checked:

            self.clear_manual_inputs()

            for i in range(self.num_columns):

                label = QLabel(f"Column {i+1}:")
                self.scroll_area.setMinimumHeight(200)
                edit = QLineEdit()

                edit.textChanged.connect(
                    self.update_preview
                )
                edit.setPlaceholderText(
                    f"Header {i+1}"
                )

                self.manual_inputs.append(edit)

                row = QHBoxLayout()
                row.addWidget(label)
                row.addWidget(edit)

                container = QWidget()
                container.setLayout(row)

                self.manual_layout.addWidget(container)

            self.scroll_area.setVisible(True)

        else:
            self.scroll_area.setVisible(False)

    def on_import(self):

        if self.manual_button.isChecked():

            headers = [
                edit.text().strip()
                for edit in self.manual_inputs
            ]

            self.options.header = None
            self.options.manual_headers = headers

        elif self.header_button.isChecked():

            self.options.header = 0

        elif self.no_header_button.isChecked():

            self.options.header = None

        elif self.file_button.isChecked():
            headers = HeaderReader().read_headers(
                filename=self.options.header_file
            )

            self.options.header = None

        else:

            self.options.header = 0

        self.accept()


    def get_options(self):
        return self.options

    def clear_manual_inputs(self):

        while self.manual_layout.count():

            item = self.manual_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.manual_inputs.clear()



    def update_options_from_ui(self):

        if self.header_button.isChecked():
            self.options.header = 0

        elif self.no_header_button.isChecked():
            self.options.header = None

        elif self.manual_button.isChecked():

                self.options.manual_headers = [
                    box.text()
                    for box in self.manual_inputs
                ]

        elif self.file_button.isChecked():
            
            self.options.header = None

        else:
            self.options.header = 0

        self.options.delimiter = (
                self.delimiter_box.currentText()
            )


    def update_preview(self):

        self.update_options_from_ui()

        df = self.reader.read(
            self.filename,
            self.options,
            preview=True
        )

        self.preview_table.display_dataframe(df)




    def select_header_file(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Header File",
            "",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
        )

        if not filename:
            return

        headers = HeaderReader().read_headers(filename)

        self.options.manual_headers = headers

        

        self.update_preview()