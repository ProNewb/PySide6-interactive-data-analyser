from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)

from core.typed_value_input import TypedValueInput


class AddRowDialog(QDialog):

    def __init__(self, dataframe, parent=None):
        super().__init__(parent)

        self.dataframe = dataframe
        self.inputs = {}

        self.setWindowTitle("Add Row")

        self.build_ui()

    def build_ui(self):

        layout = QVBoxLayout(self)

        for column in self.dataframe.columns:

            row_layout = QHBoxLayout()

            label = QLabel(str(column))

            dtype = self.dataframe[column].dtype

            input_widget = TypedValueInput(dtype)

            self.inputs[column] = input_widget

            row_layout.addWidget(label)
            row_layout.addWidget(input_widget)

            layout.addLayout(row_layout)

        buttons = QHBoxLayout()

        cancel = QPushButton("Cancel")
        add = QPushButton("Add Row")

        cancel.clicked.connect(self.reject)
        add.clicked.connect(self.accept)

        buttons.addStretch()
        buttons.addWidget(cancel)
        buttons.addWidget(add)

        layout.addLayout(buttons)

    def get_values(self):

        return {
            column: widget.get_value()
            for column, widget in self.inputs.items()
        }