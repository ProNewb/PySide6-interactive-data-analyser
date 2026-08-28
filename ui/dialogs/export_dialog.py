from dataclasses import dataclass

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


@dataclass
class ExportOptions:

    FILE_TYPES = [
        ("CSV", "csv"),
        ("Excel", "xlsx"),
        ("JSON", "json"),
        ("Parquet", "parquet"),
    ]

    workspace: object = None
    target: str = "main"
    result_index: int = -1

    file_type: str = "csv"

    delimiter: str = ","
    encoding: str = "utf-8"

    include_header: bool = True
    include_index: bool = False
    selection_only: bool = False

    def file_filter(self):

        filters = {
            "csv": "CSV Files (*.csv)",
            "xlsx": "Excel Files (*.xlsx)",
            "json": "JSON Files (*.json)",
            "parquet": "Parquet Files (*.parquet)",
        }

        return filters[self.file_type]

class ExportDialog(QDialog):

    def __init__(self, datasets, parent=None):

        super().__init__(parent)

        self.datasets = datasets
        self.options = ExportOptions()

        self.build_ui()

    def build_ui(self):

        layout = QVBoxLayout()

        # --------------------------------
        # Dataset
        # --------------------------------

        layout.addWidget(
            QLabel("Dataset")
        )

        self.dataset_box = QComboBox()

        for label, dataset in self.datasets.items():

            self.dataset_box.addItem(
                label,
                dataset
            )

        layout.addWidget(
            self.dataset_box
        )

        # --------------------------------
        # Format
        # --------------------------------

        layout.addWidget(
            QLabel("File format")
        )

        self.format_box = QComboBox()

        for label, value in ExportOptions.FILE_TYPES:

            self.format_box.addItem(
                label,
                value
            )

        layout.addWidget(
            self.format_box
        )

        # --------------------------------
        # Delimiter
        # --------------------------------

        layout.addWidget(
            QLabel("Delimiter")
        )

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
            self.delimiter_box
        )

        # --------------------------------
        # Buttons
        # --------------------------------

        buttons = QHBoxLayout()

        export_button = QPushButton("Export")
        cancel_button = QPushButton("Cancel")

        export_button.clicked.connect(
            self.on_export
        )

        cancel_button.clicked.connect(
            self.reject
        )

        buttons.addWidget(export_button)
        buttons.addWidget(cancel_button)

        layout.addLayout(buttons)

        self.setLayout(layout)

    def on_export(self):

        dataset = self.dataset_box.currentData()

        if dataset is None:

            QMessageBox.warning(
                self,
                "Export",
                "Please select a dataset."
            )

            return

        self.options.target = dataset["target"]
        self.options.workspace = dataset["workspace"]
        self.options.result_index = dataset.get(
            "result_index",
            -1
        )

        self.options.file_type = (
            self.format_box.currentData()
        )

        self.options.delimiter = (
            self.delimiter_box.currentText()
        )

        self.accept()

    def get_options(self):

        return self.options