from PySide6.QtWidgets import (
    QComboBox, QDialog, QFormLayout,
    QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QVBoxLayout
)

from core.data_processor import CalculatedColumnConfig


class CalculatedColumnDialog(QDialog):

    def __init__(self, dataframe, parent=None):
        super().__init__(parent)

        self.df = dataframe

        self.setWindowTitle("Calculated Column")
        self.resize(420, 220)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name = QLineEdit()

        self.operation = QComboBox()
        self.operation.addItems([
            "add",
            "subtract",
            "multiply",
            "divide",
            "concatenate",
            "absolute",
            "round"
        ])

        self.column_a = QComboBox()
        self.column_b = QComboBox()

        self.column_a.addItems(map(str, dataframe.columns))
        self.column_b.addItems(map(str, dataframe.columns))

        self.decimals = QSpinBox()
        self.decimals.setRange(0, 10)
        self.decimals.hide()

        form.addRow("New name", self.name)
        form.addRow("Operation", self.operation)
        form.addRow("Column A", self.column_a)
        form.addRow("Column B", self.column_b)
        form.addRow("Decimals", self.decimals)

        layout.addLayout(form)

        self.preview = QLabel()
        layout.addWidget(self.preview)

        buttons = QHBoxLayout()

        ok = QPushButton("Create")
        cancel = QPushButton("Cancel")

        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

        buttons.addStretch()
        buttons.addWidget(cancel)
        buttons.addWidget(ok)

        layout.addLayout(buttons)

        self.operation.currentTextChanged.connect(
            self.update_controls
        )

        self.column_a.currentTextChanged.connect(
            self.update_preview
        )

        self.column_b.currentTextChanged.connect(
            self.update_preview
        )

        self.name.textChanged.connect(
            self.update_preview
        )

        self.update_controls()

    def update_controls(self):

        op = self.operation.currentText()

        binary = {
            "add",
            "subtract",
            "multiply",
            "divide",
            "concatenate"
        }

        self.column_b.setVisible(op in binary)
        self.decimals.setVisible(op == "round")

        self.update_preview()

    def update_preview(self):

        name = self.name.text() or "NewColumn"

        a = self.column_a.currentText()
        b = self.column_b.currentText()

        op = self.operation.currentText()

        symbols = {
            "add": "+",
            "subtract": "-",
            "multiply": "*",
            "divide": "/",
            "concatenate": "&"
        }

        if op in symbols:
            text = f"{name} = {a} {symbols[op]} {b}"

        elif op == "absolute":
            text = f"{name} = abs({a})"

        else:
            text = f"{name} = round({a})"

        self.preview.setText(text)

    def get_config(self):

        op = self.operation.currentText()

        columns = [self.column_a.currentText()]

        value = None

        if op in (
            "add",
            "subtract",
            "multiply",
            "divide",
            "concatenate"
        ):
            columns.append(self.column_b.currentText())

        elif op == "round":
            value = self.decimals.value()

        return CalculatedColumnConfig(
            name=self.name.text().strip(),
            operation=op,
            columns=columns,
            value=value
        )