from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
    QComboBox,
)


class ResultDestinationDialog(QDialog):

    REPLACE_RESULT = "replace_result"
    CREATE_RESULT = "create_result"
    REPLACE_MAIN = "replace_main"

    def __init__(
        self,
        has_result=False,
        parent=None
    ):
        super().__init__(parent)

        self.setWindowTitle("Result Destination")

        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel("Where should the result go?")
        )

        self.destination_combo = QComboBox()

        if has_result:
            self.destination_combo.addItem(
                "Replace current result",
                self.REPLACE_RESULT
            )

        self.destination_combo.addItem(
            "Create new result",
            self.CREATE_RESULT
        )

        self.destination_combo.addItem(
            "Replace Main with result",
            self.REPLACE_MAIN
        )

        layout.addWidget(
            self.destination_combo
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def get_destination(self):
        return self.destination_combo.currentData()