from PySide6.QtWidgets import (
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QWidget
)

from PySide6.QtCore import Signal


class GroupbyRow(QWidget):

    remove_requested = Signal(object)

    def __init__(self, dataframe, parent=None):

        super().__init__(parent)

        layout = QHBoxLayout(self)

        self.column_combo = QComboBox()

        for column in dataframe.columns:
            self.column_combo.addItem(
                str(column),
                column
            )

        self.remove_button = QPushButton("Remove")

        layout.addWidget(self.column_combo)
        layout.addWidget(self.remove_button)

        self.remove_button.clicked.connect(
            lambda: self.remove_requested.emit(self)
        )

    def get_column(self):

        return self.column_combo.currentData()