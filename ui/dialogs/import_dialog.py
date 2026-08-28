from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
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
from ui.table.preview_table import PreviewTable
from core.csv_reader import CSVReader


class ImportOptions:
    """Container for all user-selected import options."""

    def __init__(self):
        # ------------------------------
        # Header options
        # ------------------------------

        self.header = 0
        self.manual_headers = None
        self.header_file = None

        # ------------------------------
        # CSV formatting
        # ------------------------------

        self.delimiter = ","

        # ------------------------------
        # Data types
        # ------------------------------

        self.infer_types = True
        self.column_types = {}


class ImportDialog(QDialog):
    """Dialog for configuring CSV import options."""

    DTYPE_OPTIONS = [
        "Auto",
        "String",
        "Integer",
        "Float",
        "Boolean",
        "Datetime",
        "Category",
    ]

    def __init__(self, filename, parent=None):
        super().__init__(parent)

        self.filename = filename



        # ------------------------------
        # Services
        # ------------------------------

        self.reader = CSVReader()
        

        self.options = ImportOptions()
        # ------------------------------
        # State
        # ------------------------------

        self.manual_inputs = []
        self.dtype_boxes = {}
        self.dtype_columns = []
        self.num_columns = 0

        self._updating_preview = False

        # ------------------------------
        # UI
        # ------------------------------
        self.preview_table = PreviewTable()
        self.preview_table.setMinimumHeight(220)
       

        self.build_ui()

        # Initial preview
        self.update_preview()

    # ==========================================================
    # UI
    # ==========================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        # ------------------------------------------------------
        # Headers
        # ------------------------------------------------------

        layout.addWidget(
            QLabel("Header")
        )

        self.button_group = QButtonGroup(self)

        self.auto_button = QRadioButton(
            "Detect automatically"
        )

        self.header_button = QRadioButton(
            "First row contains headers"
        )

        self.no_header_button = QRadioButton(
            "No headers"
        )

        self.manual_button = QRadioButton(
            "Enter headers manually"
        )

        self.file_button = QRadioButton(
            "Load headers from text file"
        )

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

        # ------------------------------------------------------
        # Header file
        # ------------------------------------------------------

        self.header_file_button = QPushButton(
            "Browse Header File..."
        )

        self.header_file_button.setEnabled(False)

        layout.addWidget(
            self.header_file_button
        )

        # ------------------------------------------------------
        # Delimiter
        # ------------------------------------------------------

        layout.addWidget(
            QLabel("Delimiter")
        )

        self.delimiter_box = QComboBox()

        self.delimiter_box.addItems([
            ",",
            ";",
            "\t",
            "|",
        ])

        layout.addWidget(
            self.delimiter_box
        )

        # ------------------------------------------------------
        # Data types
        # ------------------------------------------------------

        layout.addWidget(
            QLabel("Data types")
        )

        self.infer_types_checkbox = QCheckBox(
            "Automatically detect data types"
        )

        self.infer_types_checkbox.setChecked(True)

        layout.addWidget(
            self.infer_types_checkbox
        )

        self.dtype_scroll = QScrollArea()

        self.dtype_scroll.setWidgetResizable(True)
        self.dtype_scroll.setMinimumHeight(180)

        self.dtype_widget = QWidget()

        self.dtype_layout = QVBoxLayout(
            self.dtype_widget
        )

        self.dtype_scroll.setWidget(
            self.dtype_widget
        )

        layout.addWidget(
            self.dtype_scroll
        )

        # ------------------------------------------------------
        # Preview
        # ------------------------------------------------------

        layout.addWidget(
            QLabel("Preview")
        )
        
        layout.addWidget(self.preview_table, 1) 
        layout.addWidget(
            self.preview_table
        )

        # ------------------------------------------------------
        # Manual headers
        # ------------------------------------------------------

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(200)

        self.manual_widget = QWidget()

        self.manual_layout = QVBoxLayout(
            self.manual_widget
        )

        self.scroll_area.setWidget(
            self.manual_widget
        )

        self.scroll_area.setVisible(False)

        layout.addWidget(
            self.scroll_area
        )

        # ------------------------------------------------------
        # Preview options
        # ------------------------------------------------------

        self.show_all_rows = QCheckBox(
            "Show all rows"
        )

        layout.addWidget(
            self.show_all_rows
        )

        # ------------------------------------------------------
        # Buttons
        # ------------------------------------------------------

        buttons = QHBoxLayout()

        import_button = QPushButton(
            "Import"
        )

        cancel_button = QPushButton(
            "Cancel"
        )

        import_button.clicked.connect(
            self.on_import
        )

        cancel_button.clicked.connect(
            self.reject
        )

        buttons.addWidget(
            import_button
        )

        buttons.addWidget(
            cancel_button
        )

        layout.addLayout(
            buttons
        )

        # ======================================================
        # Connections
        # ======================================================

        self.manual_button.toggled.connect(
            self.show_manual_inputs
        )

        self.file_button.toggled.connect(
            self.header_file_button.setEnabled
        )

        self.header_file_button.clicked.connect(
            self.select_header_file
        )

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
            self.update_preview
        )

        self.delimiter_box.currentIndexChanged.connect(
            self.update_preview
        )

        self.infer_types_checkbox.toggled.connect(
            self.update_preview
        )

        self.show_all_rows.toggled.connect(
            self.update_preview
        )

    # ==========================================================
    # Header controls
    # ==========================================================

    def show_manual_inputs(self, checked):
        """Show or hide manual header controls."""

        if not checked:
            self.scroll_area.setVisible(False)
            return

        self.build_manual_inputs()

        self.scroll_area.setVisible(True)

    def build_manual_inputs(self):
        """Create the manual header controls."""

        self.clear_manual_inputs()

        for i in range(self.num_columns):

            label = QLabel(
                f"Column {i + 1}:"
            )

            edit = QLineEdit()

            edit.setPlaceholderText(
                f"Header {i + 1}"
            )

            edit.textChanged.connect(
                self.update_preview
            )

            row = QHBoxLayout()

            row.addWidget(label)
            row.addWidget(edit)

            container = QWidget()

            container.setLayout(row)

            self.manual_layout.addWidget(
                container
            )

            self.manual_inputs.append(
                edit
            )

    def clear_manual_inputs(self):
        """Remove all manual header controls."""

        while self.manual_layout.count():

            item = self.manual_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self.manual_inputs.clear()

    # ==========================================================
    # Data type controls
    # ==========================================================

    def build_dtype_controls(self, dataframe):

        previous = {
            col: box.currentText()
            for col, box in self.dtype_boxes.items()
        }

        self.clear_dtype_controls()

        for column in dataframe.columns:

            combo = QComboBox()

            combo.blockSignals(True)
            combo.addItems(self.DTYPE_OPTIONS)

            if column in previous:
                combo.setCurrentText(previous[column])

            combo.blockSignals(False)

            combo.currentTextChanged.connect(self.on_dtype_changed)

            row = QHBoxLayout()
            row.addWidget(QLabel(str(column)))
            row.addWidget(combo)

            container = QWidget()
            container.setLayout(row)

            self.dtype_layout.addWidget(container)

            self.dtype_boxes[column] = combo

        self.dtype_columns = list(dataframe.columns)

    def clear_dtype_controls(self):
        """Remove all dtype controls."""

        while self.dtype_layout.count():

            item = self.dtype_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self.dtype_boxes.clear()
        self.dtype_columns = []

    def update_dtype_controls(self, dataframe):

        columns = list(dataframe.columns)

        if columns == self.dtype_columns:
            return

        self.build_dtype_controls(dataframe)
    # ==========================================================
    # Options
    # ==========================================================

    def update_options_from_ui(self):
        """Copy the current UI state into ImportOptions."""

        # ------------------------------------------------------
        # Header
        # ------------------------------------------------------

        if self.header_button.isChecked():

            self.options.header = 0

            self.options.manual_headers = None

        elif self.no_header_button.isChecked():

            self.options.header = None

            self.options.manual_headers = None

        elif self.manual_button.isChecked():

            self.options.header = None

            self.options.manual_headers = [
                edit.text().strip()
                for edit in self.manual_inputs
            ]

        elif self.file_button.isChecked():

            self.options.header = None

        else:

            # Automatic currently means pandas' normal
            # first-row header behaviour.
            self.options.header = 0

        # ------------------------------------------------------
        # Delimiter
        # ------------------------------------------------------

        self.options.delimiter = (
            self.delimiter_box.currentText()
        )

        # ------------------------------------------------------
        # Type inference
        # ------------------------------------------------------

        self.options.infer_types = (
            self.infer_types_checkbox.isChecked()
        )

        # ------------------------------------------------------
        # Explicit column types
        # ------------------------------------------------------

        self.options.column_types = {}

        for column, combo in self.dtype_boxes.items():

            dtype = combo.currentText()

            if dtype != "Auto":

                self.options.column_types[column] = (
                    dtype
                )

    # ==========================================================
    # Preview
    # ==========================================================
    def update_preview(self):

        self.update_options_from_ui()
        full = self.show_all_rows.isChecked()
        preview = not self.show_all_rows.isChecked()

        df = self.reader.read(
            self.filename,
            self.options,
            preview=preview
        )

        self.num_columns = len(df.columns)
        self.update_dtype_controls(df)

        self.preview_table.display_dataframe(
            df,
            full=full
        )

    # ==========================================================
    # Import
    # ==========================================================

    def on_import(self):
        """Validate and accept the selected options."""

        self.update_options_from_ui()

        # Manual headers
        if self.manual_button.isChecked():

            headers = [
                edit.text().strip()
                for edit in self.manual_inputs
            ]

            if not all(headers):

                QMessageBox.warning(
                    self,
                    "Invalid Headers",
                    "Please provide a name for every column."
                )

                return

            if len(headers) != len(set(headers)):

                QMessageBox.warning(
                    self,
                    "Duplicate Headers",
                    "Column names must be unique."
                )

                return

            self.options.manual_headers = headers

        # Header file
        if self.file_button.isChecked():

            if not self.options.header_file:

                QMessageBox.warning(
                    self,
                    "No Header File",
                    "Please select a header file."
                )

                return

        self.accept()

    def get_options(self):
        """Return the completed ImportOptions object."""

        self.update_options_from_ui()

        return self.options

    # ==========================================================
    # Header file
    # ==========================================================

    def select_header_file(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Header File",
            "",
            "Text Files (*.txt);;CSV Files (*.csv)"
        )

        if not filename:
            return

        self.options.header_file = filename

        self.options.manual_headers = (
            HeaderReader().read_headers(
                filename
            )
        )

        # If the file provided headers, display
        # them in the preview immediately.
        self.update_preview()

    def on_dtype_changed(self):
        self.update_options_from_ui()

        df = self.reader.read(
            self.filename,
            self.options,
            preview=True
        )

        self.preview_table.display_dataframe(
            df,
            full=self.show_all_rows.isChecked()
        )