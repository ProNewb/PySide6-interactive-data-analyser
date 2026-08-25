from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)

from core.typed_value_input import TypedValueInput


class AddColumnDialog(QDialog):

    TYPES = {
        "String": "string",
        "Integer": "integer",
        "Float": "float",
        "Boolean": "boolean",
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add Column")

        self.build_ui()
        self.update_value_input()

    def build_ui(self):

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.name_input = QLineEdit()

        self.dtype_combo = QComboBox()

        for label in self.TYPES:
            self.dtype_combo.addItem(
                label,
                self.TYPES[label]
            )

        self.value_container = QVBoxLayout()

        form.addRow(
            "Column name:",
            self.name_input
        )

        form.addRow(
            "Data type:",
            self.dtype_combo
        )

        form.addRow(
            "Default value:",
            self.value_container
        )

        layout.addLayout(form)

        buttons = QHBoxLayout()

        cancel = QPushButton("Cancel")
        add = QPushButton("Add Column")

        cancel.clicked.connect(self.reject)
        add.clicked.connect(self.accept)

        buttons.addStretch()
        buttons.addWidget(cancel)
        buttons.addWidget(add)

        layout.addLayout(buttons)

        self.dtype_combo.currentIndexChanged.connect(
            self.update_value_input
        )

    def update_value_input(self):

        # Remove previous widget
        while self.value_container.count():

            item = self.value_container.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        dtype = self.dtype_combo.currentData()

        self.value_input = TypedValueInput(dtype)

        self.value_container.addWidget(
            self.value_input
        )

    def get_config(self):

        name = self.name_input.text().strip()

        if not name:
            raise ValueError(
                "Column name cannot be empty."
            )

        dtype = self.dtype_combo.currentData()

        value = self.value_input.get_value()

        from core.data_processor import AddColumnConfig

        return AddColumnConfig(
            name=name,
            value=value,
            dtype=dtype
        )