from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QRadioButton,
    QVBoxLayout,
    QAbstractItemView
)

from PySide6.QtCore import Qt

class SelectionToolbar(QWidget):

    def __init__(self, table):

        super().__init__()

        self.table = table

        layout = QVBoxLayout()
        title = QLabel("Selection options")
        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        
        self.cells_button = QRadioButton(
            "Cells"
        )

        self.rows_button = QRadioButton(
            "Rows"
        )

        self.columns_button = QRadioButton(
            "Columns"
        )


        layout.addWidget(
            self.cells_button
        )

        layout.addWidget(
            self.rows_button
        )

        layout.addWidget(
            self.columns_button
        )

        self.setLayout(layout)


        self.cells_button.clicked.connect(
            self.select_cells
        )

        self.rows_button.clicked.connect(
            self.select_rows
        )

        self.columns_button.clicked.connect(
            self.select_columns
        )


    def select_cells(self):

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectItems
        )


    def select_rows(self):

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )


    def select_columns(self):

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectColumns
        )