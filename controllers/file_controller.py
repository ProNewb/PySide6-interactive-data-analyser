
from tkinter import dialog

import pandas as pd
import os
import views.ui.import_dialog as import_dialog
from PySide6.QtWidgets import QFileDialog
class FileController:

    def __init__(self, dataset_manager):
        self.dataset_manager = dataset_manager

    def open_file(self):

        print("Open file called")

        filename, _ = QFileDialog.getOpenFileName(
            None,
            "Open CSV",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )

        print(filename)

        if not filename:
            print("No file selected")
            return

        dialog = import_dialog.ImportDialog()

        if dialog.exec():

            options = dialog.get_options()

            self.dataset_manager.load_csv(
                filename,
                header=options.header
            )

        print("CSV loaded!")

        print(self.dataset_manager.get_dataframe())
            
    def save_project(self):
        pass

    def export_csv(self):
        pass

    def close_project(self):
        pass