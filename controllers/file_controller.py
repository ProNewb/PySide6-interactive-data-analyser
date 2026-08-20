from PySide6.QtWidgets import QFileDialog

from views.ui.dialogs.import_dialog import ImportDialog


class FileController:
    """Handle file-related operations for the application."""

    def __init__(self, dataset_manager):

        self.dataset_manager = dataset_manager

    # ==================================================
    # OPEN
    # ==================================================

    def open_file(self):
        """Open a CSV file and pass it to the dataset manager."""

        filename, _ = QFileDialog.getOpenFileName(
            None,
            "Open CSV",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )

        # The user cancelled the file dialog.
        if not filename:
            return

        # Ask the user how the CSV should be imported.
        dialog = ImportDialog(filename)

        if not dialog.exec():
            return

        options = dialog.get_options()

        # The DatasetManager is responsible for actually loading
        # and storing the resulting DataFrame.
        self.dataset_manager.load_csv(
            filename,
            options
        )

    # ==================================================
    # FUTURE FILE OPERATIONS
    # ==================================================

    def save_project(self):
        """Save the current project state."""
        pass

    def export_csv(self):
        """Export the current dataset as a CSV file."""
        pass

    def close_project(self):
        """Close the current project."""
        pass