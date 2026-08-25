class PreviewMixin:

    def load_source(self):
        self.preview_table.display_dataframe(
            self.dataframe,
            full=self.show_all_rows.isChecked()
        )

    def get_source(self):
        if self.use_selection.isChecked():
            return self.preview_table.get_analysis_dataframe()

        return self.dataframe