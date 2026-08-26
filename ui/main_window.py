import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSpinBox,

    QTabWidget,

    QWidget,
    QLabel,
    QVBoxLayout
)



from ui.dialogs.add_column_dialog import AddColumnDialog
from ui.dialogs.add_row_dialog import AddRowDialog
from ui.dialogs.calculated_column_dialog import CalculatedColumnDialog
from ui.workspace import Workspace
from core.data_processor import AddColumnConfig, AddRowConfig, DataProcessor, DeleteColumnConfig, DeleteRowsConfig, DuplicateColumnConfig, DuplicateRowConfig, RenameColumnConfig, CalculatedColumnConfig
from ui.dialogs.transform_dialog import TransformDialog
from ui.dialogs.aggregation_dialog import AggregationDialog
from ui.dialogs.cleaning_dialog import CleaningDialog
from ui.dialogs.data_dialog import DataDialog
from ui.dialogs.join_dialog import JoinDialog
from ui.dialogs.settings_dialog import SettingsDialog
from ui.menus.main_menu import MainMenu
from ui.menus.status_bar import StatusBar
from ui.dialogs.result_destination_dialog import ResultDestinationDialog

class MainWindow(QMainWindow):
    """Main application window.
        All data modifications are delegated to DatasetManager.
         MainWindow is responsible only for dialogs and UI updates."""

    def __init__(self, settings_manager, theme_manager):

        super().__init__()

        self.settings_manager = settings_manager 
        self.theme_manager = theme_manager

        # Workspace container
        self.workspaces = QTabWidget()
        self.workspaces.setTabsClosable(True)
        self.workspaces.tabCloseRequested.connect(self.close_workspace)

        # workspace formatting

        self.workspaces.setStyleSheet("""
            QTabBar::tab {
                min-width: 100px;
                max-width: 180px;
            }
        """)


        self.theme_manager.apply_theme(
            self.settings_manager.settings
        )

        # underlying operations
        self.data_processor = DataProcessor()
        self.main_menu = MainMenu(self)

        # UI
        self.initialise_window()
        self.build_ui()

        # Create initial workspace
        self.create_workspace()

        # Workspace changes
        self.workspaces.currentChanged.connect(
            self.workspace_changed
        )

        self.rebuild_view_menu()

        # Workspace changes
        self.workspaces.currentChanged.connect(
            self.workspace_changed
        )


      

        # ----------------------------------
        # Window
        # ----------------------------------



        # ----------------------------------
        # Signals
        # ----------------------------------


        # ==================================================
        # MAIN MENU CONNECTIONS
        # ==================================================

        self.main_menu.open_action.triggered.connect(
            self.load_dataset
        )

        self.main_menu.open_project_action.triggered.connect(
            self.load_project
        )

        self.main_menu.save_project_action.triggered.connect(
            self.save_project
        )

        self.main_menu.export_data_action.triggered.connect(
            self.export_data
        )

        self.main_menu.close_file_action.triggered.connect(
            self.close_file
        )

        self.main_menu.settings_action.triggered.connect(
            self.open_options
        )

        self.main_menu.exit_action.triggered.connect(
            self.close
        )

        self.main_menu.filter_action.triggered.connect(
            self.open_filter_dialog
        )

        self.main_menu.aggregate_action.triggered.connect(
            self.open_aggregation_dialog
        )

        self.main_menu.join_action.triggered.connect(
            self.open_join_dialog
        )

        self.main_menu.transform_action.triggered.connect(
            self.open_transform_dialog
        )

        self.main_menu.clean_action.triggered.connect(
            self.open_cleaning_dialog
        )

        self.main_menu.calculated_column_action.triggered.connect(
            self.calculated_column
        )


        # ==================================================
        # MAIN MENU EDIT CONNECTIONS
        # ==================================================

        self.main_menu.rename_column_action.triggered.connect(
            self.rename_column
        )

        self.main_menu.duplicate_column_action.triggered.connect(
            self.duplicate_column
        )

        self.main_menu.add_column_action.triggered.connect(
            self.add_column
        )

        self.main_menu.delete_column_action.triggered.connect(
            self.delete_column
        )

        self.main_menu.add_row_action.triggered.connect(
            self.add_row
        )

        self.main_menu.duplicate_row_action.triggered.connect(
            self.duplicate_row
        )

        self.main_menu.delete_row_action.triggered.connect(
            self.delete_rows
        )
       
        self.main_menu.reset_action.triggered.connect(
            self.reset_operation
        )
        self.main_menu.undo_button.triggered.connect(
            self.undo_operation
        )
       # self.main_menu.result_dataset_action.triggered.connect(
        #    self.toggle_result_tab
        #)
        self.main_menu.redo_button.setEnabled(False)
        self.status = StatusBar()


        self.setStatusBar(
            self.status
        )
    # Display
    def initialise_window(self):
            if self.settings_manager.settings.start_maximized:
                self.showMaximized()
            else:
                self.resize(1200, 800)



    def build_ui(self):

        self.create_central_widget()
        self.create_title()
        self.create_content_area()
        


    def create_central_widget(self):

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

    def create_title(self):

        title = QLabel("Data Explorer")
        title.setAlignment(Qt.AlignCenter)

        self.main_layout.addWidget(title)


    def create_content_area(self):

        self.create_operation_controls()

        self.main_layout.addWidget(
            self.workspaces
        )
    def create_operation_controls(self):

        target_layout = QHBoxLayout()

        target_layout.addWidget(
            QLabel("Operate on:")
        )

        self.target_combo = QComboBox()

        self.target_combo.addItem(
            "Main Dataset",
            "main"
        )

        self.target_combo.addItem(
            "Result Dataset",
            "result"
        )

        self.use_selection = QCheckBox(
            "Use selection"
        )

        self.allow_cross_tab_selection = QCheckBox(
            "cross-tab selection"
        )
        target_layout.addWidget(
            self.target_combo
        )

        target_layout.addWidget(
            self.use_selection
        )
        target_layout.addWidget(
            self.allow_cross_tab_selection
        )
        target_layout.addStretch()

        self.main_layout.addLayout(
            target_layout
        )
    # retrieve data
    def load_dataset(self):

        current_workspace = self.workspace
        
        # Reuse the initial empty Untitled tab
        if (
            self.workspaces.count() == 1
            and current_workspace is not None
            and not current_workspace.dataset_manager.has_data()
        ):
            workspace = current_workspace
            created_new = False

        else:
            workspace = self.create_workspace("Untitled")
            created_new = True

        # Open the file
        if not workspace.file_controller.open_file():

            if created_new:

                index = self.workspaces.indexOf(workspace)

                if index >= 0:
                    self.workspaces.removeTab(index)

                workspace.deleteLater()

            return

        # Refresh only this workspace
        workspace.refresh()

        # Rename the tab
        filename = workspace.dataset_manager.filename

        if filename:
            title = Path(filename).stem
        else:
            title = "Untitled"

        index = self.workspaces.indexOf(workspace)

        if index >= 0:
            self.workspaces.setTabText(
                index,
                title
            )
            self.workspaces.setCurrentIndex(index)

        self.update_workspace_controls()

        self.status.showMessage(
            f"Loaded {title}"
        )

    def load_project(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "Project Files (*.json);;All Files (*)"
        )

        if not filename:
            return False

        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as project_file:

                project = json.load(project_file)

        except (
            OSError,
            json.JSONDecodeError
        ) as error:

            QMessageBox.warning(
                self,
                "Open Project",
                f"Could not open project:\n{error}"
            )

            return False

        saved_workspaces = project.get(
            "workspaces",
            []
        )

        if not saved_workspaces:

            QMessageBox.warning(
                self,
                "Open Project",
                "The project contains no workspaces."
            )

            return False

        # Remove the current workspaces
        while self.workspaces.count() > 0:

            widget = self.workspaces.widget(0)

            self.workspaces.removeTab(0)

            if widget is not None:
                widget.deleteLater()

        # Recreate every saved workspace
        for saved_workspace in saved_workspaces:

            name = saved_workspace.get(
                "name",
                "Untitled"
            )

            data = saved_workspace.get("data")

            if data is None:
                continue

            workspace = self.create_workspace(name)

            if not workspace.load_project_data(data):

                index = self.workspaces.indexOf(workspace)

                if index >= 0:
                    self.workspaces.removeTab(index)

                workspace.deleteLater()

                continue

        current_index = project.get(
            "current_workspace",
            0
        )

        if 0 <= current_index < self.workspaces.count():
            self.workspaces.setCurrentIndex(current_index)

        self.update_workspace_controls()

    def close_file(self):

        index = self.workspaces.currentIndex()

        if index >= 0:
            self.close_workspace(index)


    def open_filter_dialog(self, context=None):

        workspace, target, view, dataframe = self.resolve_context(context)

        if dataframe is None:
            return

        if self.use_selection.isChecked():
            dataframe = view.get_analysis_dataframe()

        dialog = DataDialog(
            self.get_available_datasets(),
            self,
            current=self.get_current_dataset_label(
    workspace,
    target
),
            use_selection=self.use_selection.isChecked()
        )
        if not dialog.exec():
            return

        workspace = dialog.get_workspace()
        target = dialog.get_target()
        dataframe = dialog.get_dataframe()

        config = dialog.get_conditions()

        try:

            result = self.data_processor.filter(
                dataframe,
                config
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Filter Failed",
                str(error)
            )

            return

        destination = self.choose_result_destination(
            workspace
        )

        if destination is None:
            return

        self.apply_result(
            workspace,
            result,
            destination=destination,
            description=config.describe(),
            result_name="Filter"
        )

        self.status.showMessage(
            config.describe()
        )

        workspace.refresh()
        self.update_workspace_controls()


    def refresh_views(self):

        workspace = self.workspace

        if workspace is None:
            return

        workspace.refresh()

        self.update_workspace_controls()
        
    def undo_operation(self):

        target = self.target_combo.currentData()

        if target in (
            "main_selection",
            "result_selection"
        ):

            QMessageBox.information(
                self,
                "Undo",
                "Undo cannot be applied directly to a selection."
            )

            return

        description = self.dataset_manager.undo(target)

        if description is not None:

            self.refresh_views()

            self.update_data_actions()

            self.status.showMessage(
                f"Undid: {description}"
            )

    def reset_operation(self):

        if not self.dataset_manager.can_reset():
            return

        result = QMessageBox.question(
            self,
            "Reset Data",
            "Are you sure you want to reset the dataset?\n\n"
            "All modifications will be removed.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if result == QMessageBox.Yes:

            if self.dataset_manager.reset():

                self.refresh_views()
                self.update_data_actions()

                self.status.showMessage(
                    "Dataset reset to original state"
                )


    def update_data_actions(self):

        target = self.target_combo.currentData()

        is_dataset = target in (
            "main",
            "result"
        )

        self.main_menu.undo_button.setEnabled(
            is_dataset
            and self.dataset_manager.can_undo(target)
        )

        self.main_menu.redo_button.setEnabled(
            is_dataset
            and self.dataset_manager.can_redo(target)
        )

        self.main_menu.reset_action.setEnabled(
            target == "main"
            and self.dataset_manager.can_reset()
        )


    def open_aggregation_dialog(self, context=None):

        workspace, target, view, dataframe = self.resolve_context(context)

        if dataframe is None:
            return

        if self.use_selection.isChecked():
            dataframe = view.get_analysis_dataframe()

        dialog = AggregationDialog(
            self.get_available_datasets(),
            self,
            current=self.get_current_dataset_label(
    workspace,
    target
),
            use_selection=self.use_selection.isChecked()
        )

        if not dialog.exec():
            return

        # Only use the clicked view's selection
        if self.use_selection.isChecked():
            dataframe = view.get_analysis_dataframe()

        config = dialog.get_aggregation()

        result = self.data_processor.aggregate(
            dataframe,
            config
        )

        destination = self.choose_result_destination(
            workspace
        )

        if destination is None:
            return

        self.apply_result(
            workspace,
            result,
            destination=destination,
            description=config.describe(),
            result_name="Aggregation"
        )
        workspace.refresh()
        self.update_workspace_controls()
        self.status.showMessage(
            "Aggregation created"
        )

    def hide_result_view(self):

        self.main_menu.result_dataset_action.setChecked(
            False
        )

        if self.workspace:
            self.workspace.result_panel.hide()

    def hide_main_view(self):

        self.main_menu.main_dataset_action.setChecked(
            False
        )

        if self.workspace:
            self.workspace.main_view.hide()

    def toggle_main_dataset(self, checked):

        workspace = self.workspace

        if workspace is None:
            return

        workspace.set_main_visible(checked)


    def toggle_result_tab(self, index, checked):

        workspace = self.workspace

        if workspace is None:
            return

        if checked:

            workspace.result_panel.show_result(index)
            workspace.set_result_visible(True)

        else:

            workspace.set_result_visible(False)

        self.update_workspace_controls()
            

    def open_cleaning_dialog(self, context=None):

        workspace, target, view, dataframe = self.resolve_context(context)

        if dataframe is None:
            return

        dialog = CleaningDialog(
            self.get_available_datasets(),
            self,
            current=self.get_current_dataset_label(
                workspace,
                target
            ),
            use_selection=self.use_selection.isChecked()
        )

        if not dialog.exec():
            return

        workspace = dialog.get_workspace()
        target = dialog.get_target()
        result = dialog.get_result()

        if result is None:
            QMessageBox.warning(
                self,
                "Cleaning Failed",
                "No cleaning result was produced."
            )
            return

        config = dialog.get_operation()

        destination = self.choose_result_destination(
            workspace
        )

        if destination is None:
            return

        self.apply_result(
            workspace,
            result,
            destination=destination,
            description=config.describe(),
            result_name="Cleaned Data"
        )

        self.status.showMessage(
            "Cleaning completed"
        )

        workspace.refresh()
        self.update_workspace_controls()

        self.status.showMessage(
            "Cleaning completed"
        )

    def open_options(self):

        dialog = SettingsDialog(
            self.settings_manager,
            self.theme_manager,
            self
        )

        dialog.exec()

    def confirm_result_overwrite(self):

        if (
            self.dataset_manager
            .get_result_dataframe()
            is None
        ):
            return True

        answer = QMessageBox.question(
            self,
            "Overwrite Result?",
            "A result dataset already exists.\n\n"
            "Do you want to replace it?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        return answer == QMessageBox.Yes



    def redo_operation(self):

        target = self.target_combo.currentData()

        if target in (
            "main_selection",
            "result_selection"
        ):

            QMessageBox.information(
                self,
                "Redo",
                "Redo cannot be applied directly to a selection."
            )

            return

        description = self.dataset_manager.redo(
            target
        )

        if description is not None:

            self.refresh_views()

            self.status.showMessage(
                f"Redid: {description}"
            )


    def update_history_menus(self):

        target = self.target_combo.currentData()

        # Only datasets have history
        if target not in ("main", "result"):

            self.main_menu.undo_history_menu.clear()
            self.main_menu.redo_history_menu.clear()
            return

        # ---------------- Undo ----------------

        undo_menu = self.main_menu.undo_history_menu
        undo_menu.clear()

        history = self.dataset_manager.get_undo_history(target)

        for i, operation in enumerate(reversed(history), 1):

            text = f"{i}. {operation.description}"

            action = undo_menu.addAction(text)

            action.triggered.connect(
                lambda checked=False, steps=i: self.undo_multiple(steps)
            )

        # ---------------- Redo ----------------

        redo_menu = self.main_menu.redo_history_menu
        redo_menu.clear()

        history = self.dataset_manager.get_redo_history(target)

        for i, operation in enumerate(reversed(history), 1):

            text = f"{i}. {operation.description}"

            action = redo_menu.addAction(text)

            action.triggered.connect(
                lambda checked=False, steps=i: self.redo_multiple(steps)
            )
    def undo_multiple(self, steps):

        for _ in range(steps):
            self.undo_operation()


    def redo_multiple(self, steps):

        for _ in range(steps):
            self.redo_operation()

    def open_join_dialog(self, context=None):

        workspace, target, view, dataframe = self.resolve_context(context)

        if dataframe is None:
            return

        if self.use_selection.isChecked():
            dataframe = view.get_analysis_dataframe()

        dialog = JoinDialog(
            self.get_available_datasets(),
            self,
            current=self.get_current_dataset_label(
    workspace,
    target
),
            use_selection=self.use_selection.isChecked()
        )

        if not dialog.exec():
            return

        left_df = dialog.get_left_dataframe()
        right_df = dialog.get_right_dataframe()

        # Apply selection only to the dataset that launched the dialog
        if self.use_selection.isChecked():
            if dialog.get_left_workspace() is workspace:
                left_df = view.get_analysis_dataframe()

            if dialog.get_right_workspace() is workspace:
                right_df = view.get_analysis_dataframe()

        config = dialog.get_config()

        result = self.data_processor.join(
            left_df,
            right_df,
            config
        )

        destination = self.choose_result_destination(
            workspace
        )

        if destination is None:
            return

        self.apply_result(
            workspace,
            result,
            destination=destination,
            description=config.describe(),
            result_name="Join"
        )


        workspace.refresh()
        self.update_workspace_controls()

        self.status.showMessage(
            "Join completed"
        )
        
    def open_transform_dialog(self, context=None):

        workspace, target, view, dataframe = self.resolve_context(context)

        if dataframe is None:
            return

        dialog = TransformDialog(
            self.get_available_datasets(),
            self,
            current=self.get_current_dataset_label(
                workspace,
                target
            ),
            use_selection=self.use_selection.isChecked()
        )

        if not dialog.exec():
            return

        workspace = dialog.get_workspace()
        target = dialog.get_target()
        result = dialog.get_result()

        if result is None:
            QMessageBox.warning(
                self,
                "Transform Failed",
                "No transform result was produced."
            )
            return

        config = dialog.get_transform()

        destination = self.choose_result_destination(
            workspace
        )

        if destination is None:
            return

        self.apply_result(
            workspace,
            result,
            destination=destination,
            description=config.describe(),
            result_name="Transform"
        )

        self.status.showMessage(
            "Transform completed"
        )

        workspace.refresh()
        self.update_workspace_controls()

        self.status.showMessage(
            "Transform completed"
        )


    def get_dataframe_for_target(self, target, use_selection=None):

        workspace = self.workspace

        if workspace is None:
            return None

        if target == "main":

            dataframe = (
                workspace.dataset_manager.get_dataframe()
            )

            view = workspace.main_view

        elif target == "result":

            dataframe = (
                workspace.dataset_manager.get_result_dataframe()
            )

            view = workspace.result_panel.current_view()

        else:
            return None

        if dataframe is None:
            return None

        if use_selection is None:
            use_selection = self.use_selection.isChecked()

        if use_selection and view is not None:
            return view.get_analysis_dataframe()

        return dataframe
    
    def get_dialog_dataframe(self):
        """Return the current target dataframe."""

        target = self.target_combo.currentData()

        dataframe = self.get_dataframe_for_target(target)

        return target, dataframe

    def create_workspace(self, title="Untitled"):

        workspace = Workspace(self)

        self.connect_workspace_signals(workspace)

        index = self.workspaces.addTab(
            workspace,
            title
        )

        self.workspaces.setCurrentIndex(index)

        return workspace
    
    def save_project(self):

        workspaces = []

        for index in range(self.workspaces.count()):

            workspace = self.workspaces.widget(index)

            if workspace is None:
                continue

            data = workspace.get_project_data()

            if data is None:
                continue

            workspaces.append({
                "name": self.workspaces.tabText(index),
                "data": data
            })

        if not workspaces:
            QMessageBox.information(
                self,
                "Save Project",
                "There are no datasets to save."
            )
            return False

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project",
            "",
            "Project Files (*.json);;All Files (*)"
        )

        if not filename:
            return False

        if not filename.lower().endswith(".json"):
            filename += ".json"

        project = {
            "version": 4,
            "current_workspace": self.workspaces.currentIndex(),
            "workspaces": workspaces
        }

        try:

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as project_file:

                json.dump(
                    project,
                    project_file,
                    indent=2,
                    default=str
                )

        except OSError as error:

            QMessageBox.warning(
                self,
                "Save Project",
                f"Could not save the project:\n{error}"
            )

            return False

        self.status.showMessage(
            f"Project saved: {Path(filename).name}"
        )

        return True


    def export_data(self):

        if self.workspace is None:
            return

        self.workspace.export_csv()

    @property
    def workspace(self):
        """Return the currently active workspace."""

        return self.workspaces.currentWidget()


    @property
    def dataset_manager(self):
        """Return the active workspace's DatasetManager."""

        workspace = self.workspace

        if workspace is None:
            return None

        return workspace.dataset_manager


    @property
    def main_view(self):
        """Return the active workspace's main view."""

        workspace = self.workspace

        if workspace is None:
            return None

        return workspace.main_view


    @property
    def result_view(self):

        workspace = self.workspace

        if workspace is None:
            return None

        return workspace.result_panel.current_view()

    def workspace_changed(self, index):

        if index < 0:
            return

        workspace = self.workspaces.widget(index)

        if workspace is None:
            return

        self.update_workspace_controls()

    def close_workspace(self, index):

        workspace = self.workspaces.widget(index)

        if workspace is None:
            return

        # If there is data, ask before closing
        if workspace.dataset_manager.has_data():

            answer = QMessageBox.question(
                self,
                "Close Dataset",
                "Close this dataset?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if answer != QMessageBox.Yes:
                return

        self.workspaces.removeTab(index)

        workspace.deleteLater()

        # Keep at least one empty workspace
        if self.workspaces.count() == 0:
            self.create_workspace("Untitled")
        self.update_workspace_controls()

    def update_workspace_controls(self):

        workspace = self.workspace

        if workspace is None:
            return

        manager = workspace.dataset_manager

        self.main_menu.main_dataset_action.blockSignals(True)

        self.main_menu.main_dataset_action.setChecked(
            workspace.main_view.isVisible()
        )

        self.main_menu.main_dataset_action.blockSignals(False)

        self.update_data_actions()
        self.update_history_menus()
        self.rebuild_view_menu()


    @property
    def file_controller(self):

        workspace = self.workspace

        if workspace is None:
            return None

        return workspace.file_controller

    def get_available_datasets(self):

        datasets = {}

        for workspace_index in range(self.workspaces.count()):

            ws = self.workspaces.widget(workspace_index)

            if ws is None:
                continue

            workspace_name = self.workspaces.tabText(
                workspace_index
            )

            # -------------------------
            # Main
            # -------------------------

            dataframe = ws.dataset_manager.get_dataframe()

            if dataframe is not None:

                datasets[f"{workspace_name} • Main"] = {
                    "workspace": ws,
                    "target": "main",
                    "dataframe": dataframe,
                    "view": ws.main_view,
                    "result_index": None,
                }

            # -------------------------
            # Results
            # -------------------------

            for result_index, result in enumerate(
                ws.dataset_manager.results
            ):

                datasets[
                    f"{workspace_name} • {result.name}"
                ] = {
                    "workspace": ws,
                    "target": "result",
                    "dataframe": result.dataframe,
                    "view": ws.result_panel.view_at(result_index),
                    "result_index": result_index,
                }

        return datasets

    def rename_column(self, context=None):

        workspace, target, view, dataframe = self.resolve_context(context)

        if dataframe is None:
            return

        column = (
            context.get("column")
            if isinstance(context, dict)
            else view.table.selected_column()
        )

        if column is None:
            QMessageBox.warning(
                self,
                "Rename Column",
                "Please select a column first."
            )
            return

        new_name, ok = QInputDialog.getText(
            self,
            "Rename Column",
            "New name:",
            text=str(column)
        )

        if not ok or not new_name.strip():
            return

        config = RenameColumnConfig(
            old_name=column,
            new_name=new_name.strip()
        )

        try:
            result = self.data_processor.rename_column(
                dataframe,
                config
            )
        except ValueError as error:
            QMessageBox.warning(
                self,
                "Rename Column",
                str(error)
            )
            return

        if target == "main":
            workspace.dataset_manager.set_dataframe(
                result,
                config.describe()
            )
        else:
            workspace.dataset_manager.set_result_dataframe(
                result,
                config.describe()
            )

        workspace.refresh()
        self.update_workspace_controls()

        self.status.showMessage(
            config.describe()
        )

    def delete_rows(self, context=None):

        workspace, target, view, dataframe = self.resolve_context(context)

        if dataframe is None:
            return

        if isinstance(context, dict):

            row = context.get("row")
            rows = [row] if row is not None else []

        else:

            rows = view.table.selected_rows()

        if not rows:

            QMessageBox.warning(
                self,
                "Delete Rows",
                "Please select one or more rows first."
            )

            return

        answer = QMessageBox.question(
            self,
            "Delete Rows",
            f"Delete {len(rows)} selected row(s)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        config = DeleteRowsConfig(
            rows=rows
        )

        try:

            result = self.data_processor.delete_rows(
                dataframe,
                config
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Delete Rows",
                str(error)
            )

            return

        if target == "main":

            workspace.dataset_manager.set_dataframe(
                result,
                config.describe()
            )

        else:

            workspace.dataset_manager.set_result_dataframe(
                result,
                config.describe()
            )

        workspace.refresh()
        self.update_workspace_controls()

        self.status.showMessage(
            config.describe()
        )

    def add_column(self, context=None):

        workspace, target, view, dataframe = self.resolve_context(context)

        if dataframe is None:

            QMessageBox.warning(
                self,
                "Add Column",
                "There is no dataset available."
            )

            return

        dialog = AddColumnDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:

            config = dialog.get_config()

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Add Column",
                str(error)
            )

            return

        try:

            result = self.data_processor.add_column(
                dataframe,
                config
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Add Column",
                str(error)
            )

            return

        if target == "main":

            workspace.dataset_manager.set_dataframe(
                result,
                config.describe()
            )

        else:

            workspace.dataset_manager.set_result_dataframe(
                result,
                config.describe()
            )

        workspace.refresh()
        self.update_workspace_controls()

        self.status.showMessage(
            config.describe()
        )

    def duplicate_column(self, context=None):

        workspace, target, view, dataframe = self.resolve_context(context)

        if dataframe is None:
            return

        if isinstance(context, dict):
            column = context.get("column")
        else:
            column = view.table.selected_column()

        if column is None:

            QMessageBox.warning(
                self,
                "Duplicate Column",
                "Please select a column first."
            )

            return

        new_name, ok = QInputDialog.getText(
            self,
            "Duplicate Column",
            "New column name:",
            text=f"{column}_copy"
        )

        if not ok:
            return

        new_name = new_name.strip()

        if not new_name:
            return

        config = DuplicateColumnConfig(
            source=column,
            new_name=new_name
        )

        try:

            result = self.data_processor.duplicate_column(
                dataframe,
                config
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Duplicate Column",
                str(error)
            )

            return

        if target == "main":

            workspace.dataset_manager.set_dataframe(
                result,
                config.describe()
            )

        else:

            workspace.dataset_manager.set_result_dataframe(
                result,
                config.describe()
            )

        workspace.refresh()
        self.update_workspace_controls()

        self.status.showMessage(
            config.describe()
        )
        
    def delete_column(self, context=None):

        workspace, target, view, dataframe = self.resolve_context(context)

        if dataframe is None:
            return

        if isinstance(context, dict):
            columns = [context.get("column")]
            columns = [c for c in columns if c is not None]
        else:
            columns = view.table.selected_columns()

        if not columns:

            QMessageBox.warning(
                self,
                "Delete Columns",
                "Please select one or more columns first."
            )

            return

        answer = QMessageBox.question(
            self,
            "Delete Columns",
            f"Delete {len(columns)} selected column(s)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        config = DeleteColumnConfig(
            columns=columns
        )

        try:

            result = self.data_processor.delete_column(
                dataframe,
                config
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Delete Columns",
                str(error)
            )

            return

        if target == "main":

            workspace.dataset_manager.set_dataframe(
                result,
                config.describe()
            )

        else:

            workspace.dataset_manager.set_result_dataframe(
                result,
                config.describe()
            )

        workspace.refresh()
        self.update_workspace_controls()

        self.status.showMessage(
            config.describe()
        )

    def duplicate_row(self, context=None):

        workspace, target, view, dataframe = self.resolve_context(context)

        if dataframe is None:
            return

        if isinstance(context, dict):

            row = context.get("row")
            rows = [row] if row is not None else []

        else:

            rows = view.table.selected_rows()

        if not rows:

            QMessageBox.warning(
                self,
                "Duplicate Rows",
                "Please select one or more rows first."
            )

            return

        config = DuplicateRowConfig(
            rows=rows
        )

        try:

            result = self.data_processor.duplicate_rows(
                dataframe,
                config
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Duplicate Rows",
                str(error)
            )

            return

        if target == "main":

            workspace.dataset_manager.set_dataframe(
                result,
                config.describe()
            )

        else:

            workspace.dataset_manager.set_result_dataframe(
                result,
                config.describe()
            )

        workspace.refresh()
        self.update_workspace_controls()

        self.status.showMessage(
            config.describe()
        )

    def add_row(self, context=None):

        workspace, target, view, dataframe = self.resolve_context(context)

        if dataframe is None:

            QMessageBox.warning(
                self,
                "Add Row",
                "There is no dataset available."
            )

            return

        dialog = AddRowDialog(
            dataframe,
            self
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        values = dialog.get_values()

        config = AddRowConfig(
            values=values
        )

        try:

            result = self.data_processor.add_row(
                dataframe,
                config
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Add Row Failed",
                str(error)
            )

            return

        if target == "main":

            workspace.dataset_manager.set_dataframe(
                result,
                config.describe()
            )

        else:

            workspace.dataset_manager.set_result_dataframe(
                result,
                config.describe()
            )

        workspace.refresh()
        self.update_workspace_controls()

        self.status.showMessage(
            config.describe()
        )

    def calculated_column(self, context=None):

        workspace, target, view, dataframe = self.resolve_context(context)

        if dataframe is None:
            return

        dialog = CalculatedColumnDialog(
            dataframe,
            self
        )

        if dialog.exec() != QDialog.Accepted:
            return

        try:

            config = dialog.get_config()

            result = self.data_processor.add_calculated_column(
                dataframe,
                config
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Calculated Column",
                str(error)
            )

            return

        destination = self.choose_result_destination(
            workspace
        )

        if destination is None:
            return

        self.apply_result(
            workspace,
            result,
            destination=destination,
            description=config.describe(),
            result_name="Calculated Column"
        )

        self.status.showMessage(
            config.describe()
        )
        workspace.refresh()
        self.update_workspace_controls()



    def resolve_context(self, context=None):
        """
        Resolve the workspace, target, view and dataframe.

        Context menu:
            Uses the DatasetView that generated the context.

        Main menu / toolbar:
            Uses the currently selected workspace and target_combo.
        """

        # ----------------------------------------
        # Context menu
        # ----------------------------------------

        if isinstance(context, dict):

            workspace = context.get("workspace")
            target = context.get("target")
            view = context.get("view")

            if workspace is None:
                raise ValueError(
                    "Context menu did not provide a workspace."
                )

            if target not in ("main", "result"):
                raise ValueError(
                    f"Invalid context target: {target}"
                )

            if view is None:

                if target == "main":
                    view = workspace.main_view

                else:
                    view = workspace.result_panel.current_view()

            if target == "main":
                dataframe = workspace.dataset_manager.get_dataframe()
            else:
                dataframe = workspace.dataset_manager.get_result_dataframe()

            return workspace, target, view, dataframe

        # ----------------------------------------
        # Main menu / toolbar
        # ----------------------------------------

        workspace = self.workspace

        if workspace is None:
            return None, None, None, None

        target = self.target_combo.currentData()

        if target == "main":

            view = workspace.main_view
            dataframe = workspace.dataset_manager.get_dataframe()

        elif target == "result":

            view = workspace.result_panel.current_view()

            dataframe = (
                workspace.dataset_manager.get_result_dataframe()
            )

        else:

            return None, None, None, None

        return workspace, target, view, dataframe

    def connect_workspace_signals(self, workspace):

        self.connect_dataset_view(
            workspace.main_view
        )

        workspace.result_panel.result_added.connect(
            self.connect_dataset_view
        )

        workspace.result_panel.result_added.connect(
            lambda view: self.rebuild_view_menu()
        )

        workspace.result_panel.result_removed.connect(
            lambda view: self.rebuild_view_menu()
        )

        workspace.result_panel.tabs.currentChanged.connect(
            lambda index:
                self.rebuild_view_menu()
        )

    def connect_dataset_view(self, view):

        view.filter_requested.connect(
            self.open_filter_dialog
        )

        view.aggregate_requested.connect(
            self.open_aggregation_dialog
        )

        view.join_requested.connect(
            self.open_join_dialog
        )

        view.transform_requested.connect(
            self.open_transform_dialog
        )

        view.clean_requested.connect(
            self.open_cleaning_dialog
        )

        view.rename_column_requested.connect(
            self.rename_column
        )

        view.duplicate_column_requested.connect(
            self.duplicate_column
        )

        view.add_column_requested.connect(
            self.add_column
        )

        view.delete_column_requested.connect(
            self.delete_column
        )

        view.calculated_column_requested.connect(
            self.calculated_column
        )

        view.add_row_requested.connect(
            self.add_row
        )

        view.duplicate_row_requested.connect(
            self.duplicate_row
        )

        view.delete_row_requested.connect(
            self.delete_rows
        )
        
    def get_current_dataset_label(self, workspace, target):

        index = self.workspaces.indexOf(workspace)

        if index < 0:
            return None

        workspace_name = self.workspaces.tabText(index)

        if target == "main":
            return f"{workspace_name} • Main"

        if target == "result":

            result_index = (
                workspace.result_panel.current_index()
            )

            if result_index < 0:
                return None

            result_name = (
                workspace.dataset_manager.get_result_name(
                    result_index
                )
            )

            return f"{workspace_name} • {result_name}"

        return None

    def get_context_dataset(self, context):

        workspace = context["workspace"]
        target = context["target"]

        if target == "main":
            dataframe = workspace.dataset_manager.get_dataframe()
        elif target == "result":
            dataframe = workspace.dataset_manager.get_result_dataframe()
        else:
            raise ValueError(
                f"Invalid dataset target: {target}"
            )

        if dataframe is None:
            raise ValueError(
                "The selected dataset is no longer available."
            )

        return workspace, target, dataframe

 
    def rebuild_view_menu(self):

        menu = self.main_menu.view_menu

        # Remove previous result submenu
        if hasattr(self, "_result_menu"):
            menu.removeAction(
                self._result_menu.menuAction()
            )
            self._result_menu.deleteLater()

        workspace = self.workspace

        if workspace is None:
            return

        # Main
        self.main_menu.main_dataset_action.blockSignals(True)

        self.main_menu.main_dataset_action.setChecked(
            workspace.main_view.isVisible()
        )

        self.main_menu.main_dataset_action.blockSignals(False)

        # Results
        result_menu = QMenu(
            "Result Datasets",
            menu
        )

        self._result_menu = result_menu

        for index, view in enumerate(
            workspace.result_panel.views()
        ):

            action = result_menu.addAction(
                workspace.result_panel.tab_title(index)
            )

            action.setCheckable(True)

            action.setChecked(
                workspace.result_panel.isVisible()
                and workspace.result_panel.current_index() == index
            )

            action.triggered.connect(
                lambda checked=False, i=index:
                    self.toggle_result_tab(i, checked)
            )

        menu.addMenu(result_menu)

    def apply_result(
        self,
        workspace,
        dataframe,
        destination,
        description="Result created",
        result_name="Result"
    ):

        if dataframe is None:
            return False

        manager = workspace.dataset_manager

        # --------------------------------
        # Replace Main
        # --------------------------------

        if destination == ResultDestinationDialog.REPLACE_MAIN:

            manager.set_dataframe(
                dataframe,
                description
            )

            workspace.refresh()
            self.update_workspace_controls()

            return True

        # --------------------------------
        # Create Result
        # --------------------------------

        if destination == ResultDestinationDialog.CREATE_RESULT:

            workspace.create_result(
                dataframe,
                name=result_name,
                description=description
            )

            workspace.refresh()
            self.update_workspace_controls()

            return True

        # --------------------------------
        # Replace current Result
        # --------------------------------

        if destination == ResultDestinationDialog.REPLACE_RESULT:

            index = workspace.result_panel.current_index()

            if index < 0:
                QMessageBox.warning(
                    self,
                    "Replace Result",
                    "There is no current result to replace."
                )
                return False

            manager.replace_result(
                dataframe,
                description,
                index=index
            )

            workspace.refresh()
            self.update_workspace_controls()

            return True

        QMessageBox.warning(
            self,
            "Result Destination",
            f"Unknown result destination: {destination}"
        )

        return False

    def choose_result_destination(self, workspace):
        """Ask the user where an operation result should be stored."""

        has_result = (
            workspace.dataset_manager.has_results()
        )

        dialog = ResultDestinationDialog(
            has_result=has_result,
            parent=self
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        return dialog.get_destination()