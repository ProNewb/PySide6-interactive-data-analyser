
import pandas as pd
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

        self.dataset_manager.load_csv(filename)

        print("CSV loaded!")

        print(self.dataset_manager.get_dataframe())
            
    def save_project(self):
        pass

    def export_csv(self):
        pass

    def close_project(self):
        pass