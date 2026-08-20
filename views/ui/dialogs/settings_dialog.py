from copy import deepcopy

from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QWidget
)

from PySide6.QtCore import Qt

from core.column_selector import ColumnSelector
from core.data_clearner import DataCleaner, MissingValueOptions, DuplicateOptions
from core.condition_group import ConditionGroup
from core.conditions import Condition
from core.csv_reader import CSVReader
from core.dataset_table import DataTable
from views.ui.stats.cleaning_stats import CleaningStats
from views.ui.condition_row import ConditionRow
from views.ui.dialogs.import_dialog import ImportOptions
from views.ui.preview_table import PreviewTable
from analysis.data_summary import DataSummary
from PySide6.QtWidgets import QFormLayout, QSpinBox
from PySide6.QtGui import QFontDatabase, QStyleHints
class SettingsDialog(QDialog):

    THEMES = {
        "Dark Teal": "dark_teal.xml",
        "Dark Blue": "dark_blue.xml",
        "Dark Purple": "dark_purple.xml",
        "Light Teal": "light_teal.xml",
        "Light Blue": "light_blue.xml",
        "Light Purple": "light_purple.xml"
    }
    ACCENTS = {
    "Teal": "#009688",
    "Blue": "#2196F3",
    "Purple": "#9C27B0",
    "Green": "#4CAF50",
    "Orange": "#FF9800",
    "Red": "#F44336"
}
    def __init__(
    self,
    settings_manager,
    theme_manager,
    parent=None
):

        super().__init__(parent)

        self.settings_manager = settings_manager
        self.theme_manager = theme_manager

        self.setup_ui()

        # Populate themes
        for name, filename in self.THEMES.items():

            self.theme_combo.addItem(
                name,
                filename
            )

        # Store original settings
        from copy import deepcopy

        self.original_settings = deepcopy(
            self.settings_manager.settings
        )

        # Load current settings into UI
        self.load_settings()

        # Signals
        self.apply_button.clicked.connect(
            self.apply_settings
        )

        self.cancel_button.clicked.connect(
            self.cancel_settings
        )

        self.theme_combo.currentIndexChanged.connect(
            self.preview_theme
        )

        self.font_spin.valueChanged.connect(
            self.preview_theme
        )
    def load_settings(self):

        settings = self.settings_manager.settings

        index = self.theme_combo.findData(
            settings.theme
        )

        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        index = self.accent_combo.findData(
            settings.accent
        )

        if index >= 0:
            self.accent_combo.setCurrentIndex(
                index
            )
            
        index = self.font_combo.findText(
            settings.font_family
        )

        if index >= 0:
            self.font_combo.setCurrentIndex(index)

        self.font_spin.setValue(
            settings.font_size
        )

        self.maximized_checkbox.setChecked(
            settings.start_maximized
        )
    def apply_settings(self):

        settings = self.settings_manager.settings

        settings.theme = (
            self.theme_combo.currentData()
        )
        settings.accent = (
            self.accent_combo.currentData()
        )
        settings.font_family = (
            self.font_combo.currentText()
        )

        settings.font_size = (
            self.font_spin.value()
        )

        settings.start_maximized = (
            self.maximized_checkbox.isChecked()
        )

        self.theme_manager.apply_theme(
            settings
        )

        self.settings_manager.save_settings()

        self.accept()

    def preview_theme(self):

        preview_settings = deepcopy(
            self.settings_manager.settings
        )

        preview_settings.theme = (
            self.theme_combo.currentData()
        )
        preview_settings.accent = (
            self.accent_combo.currentData()
        )
        preview_settings.font_size = (
            self.font_spin.value()
        )

        self.theme_manager.apply_theme(
            preview_settings
        )

    def cancel_settings(self):

        self.settings_manager.settings.theme = (
            self.original_settings.theme
        )

        self.settings_manager.settings.font_size = (
            self.original_settings.font_size
        )

        self.settings_manager.settings.start_maximized = (
            self.original_settings.start_maximized
        )

        self.theme_manager.apply_theme(
            self.settings_manager.settings
        )

        self.reject()

    def setup_ui(self):

        self.setWindowTitle("Settings")

        self.resize(400, 250)

        # ----------------------------------
        # Main layout
        # ----------------------------------

        layout = QVBoxLayout()

        # ----------------------------------
        # Appearance
        # ----------------------------------

        appearance_label = QLabel("Appearance")

        layout.addWidget(
            appearance_label
        )

        form_layout = QFormLayout()

        # ----------------------------------
        # Theme
        # ----------------------------------

        self.theme_combo = QComboBox()

        form_layout.addRow(
            "Theme:",
            self.theme_combo
        )
        # --------------------------------
        # Theme accent 
        # --------------------------------
        
        self.accent_combo = QComboBox()

        for name, colour in self.ACCENTS.items():

            self.accent_combo.addItem(
                name,
                colour
            )

        form_layout.addRow(
            "Accent:",
            self.accent_combo
        )
        self.font_combo = QComboBox()
        # ---------------------------------
        # Font family
        # ---------------------------------


        fonts = QFontDatabase.families()

        self.font_combo.addItems(
            sorted(fonts)
        )

        form_layout.addRow(
            "Font:",
            self.font_combo
        )
        # ----------------------------------
        # Font size
        # ----------------------------------

        self.font_spin = QSpinBox()

        self.font_spin.setRange(8, 24)

        self.font_spin.setSingleStep(1)

        form_layout.addRow(
            "Font size:",
            self.font_spin
        )

        # ----------------------------------
        # Start maximised
        # ----------------------------------

        self.maximized_checkbox = QCheckBox(
            "Start application maximised"
        )

        form_layout.addRow(
            "",
            self.maximized_checkbox
        )

        layout.addLayout(
            form_layout
        )

        layout.addStretch()

        # ----------------------------------
        # Buttons
        # ----------------------------------

        button_layout = QHBoxLayout()

        self.apply_button = QPushButton(
            "Apply"
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )

        button_layout.addStretch()

        button_layout.addWidget(
            self.apply_button
        )

        button_layout.addWidget(
            self.cancel_button
        )

        layout.addLayout(
            button_layout
        )

        self.setLayout(
            layout
        )