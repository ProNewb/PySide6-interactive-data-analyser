from PySide6.QtWidgets import QFileDialog

def select_header_file(self):

    filename, _ = QFileDialog.getOpenFileName(
        self,
        "Select Header File",
        "",
        "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
    )

    if not filename:
        return

    self.options.header_file = filename

    self.update_preview()