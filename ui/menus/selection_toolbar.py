from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QWidget,
    QRadioButton,
    QVBoxLayout,
    QAbstractItemView
)

from PySide6.QtCore import Qt

class SelectionToolbar(QWidget):
    '''Side toolbar to enable different selection methods'''
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
        self.select_all_button = QPushButton(
            "Select All"
        )
        self.clear_all_button = QPushButton(
            "Clear Selection"
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
        layout.addWidget(
            self.select_all_button
        )
        layout.addWidget(
            self.clear_all_button
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
        self.select_all_button.clicked.connect(
            self.select_all
        )
        self.clear_all_button.clicked.connect(
            self.clear_selection
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

    def select_all(self):
        self.table.selectAll()

    def clear_selection(self):
        self.table.clearSelection()