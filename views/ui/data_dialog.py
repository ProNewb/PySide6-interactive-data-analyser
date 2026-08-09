from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton
)


class DataDialog(QDialog):

    def __init__(self, dataframe, parent=None):

        super().__init__(parent)

        self.dataframe = dataframe

        self.setWindowTitle("Filter Data")

        layout = QVBoxLayout()

        # Column
        layout.addWidget(
            QLabel("Column")
        )

        self.column_combo = QComboBox()

        for column in dataframe.columns:
            self.column_combo.addItem(
                str(column),
                userData=column
            )

        layout.addWidget(
            self.column_combo
        )

        # Condition
        layout.addWidget(
            QLabel("Condition")
        )

        self.condition_combo = QComboBox()

        self.condition_combo.addItems([
            "Equals",
            "Not equal",
            "Contains",
            "Greater than",
            "Less than",
            "Greater or equal",
            "Less or equal"
        ])

        layout.addWidget(
            self.condition_combo
        )

        # Value
        layout.addWidget(
            QLabel("Value")
        )

        self.value_input = QLineEdit()

        layout.addWidget(
            self.value_input
        )

        # Apply
        self.apply_button = QPushButton(
            "Apply"
        )

        layout.addWidget(
            self.apply_button
        )

        self.setLayout(layout)
        self.apply_button.clicked.connect(self.accept)

    def get_filter(self):

        return {
            "column": self.column_combo.currentData(),
            "operator": self.condition_combo.currentText(),
            "value": self.value_input.text()
        }