from copy import deepcopy

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton
)


from ui.helpers.font_delegate import FontDelegate

from PySide6.QtWidgets import QFormLayout, QSpinBox

class SettingsDialog(QDialog):
    DEFAULT_SETTINGS = {
        "highlight_color": "#FFFF00",
    }
    THEMES = {
        # Existing
        "Dark Teal": "dark_teal.xml",
        "Dark Blue": "dark_blue.xml",
        "Dark Purple": "dark_purple.xml",
        "Light Teal": "light_teal.xml",
        "Light Blue": "light_blue.xml",
        "Light Purple": "light_purple.xml",

        # Additional Dark Themes
        "Dark Cyan": "dark_cyan.xml",
        "Dark Pink": "dark_pink.xml",
        "Dark Red": "dark_red.xml",
        "Dark Amber": "dark_amber.xml",
        "Dark Lime": "dark_lime.xml",
        "Dark Yellow": "dark_yellow.xml",
        "Dark Orange": "dark_orange.xml",

        # Additional Light Themes
        "Light Cyan": "light_cyan.xml",
        "Light Pink": "light_pink.xml",
        "Light Red": "light_red.xml",
        "Light Amber": "light_amber.xml",
        "Light Lime": "light_lime.xml",
        "Light Yellow": "light_yellow.xml",
        "Light Orange": "light_orange.xml"
    }

    ACCENTS = {
        # Existing
        "Teal": "#009688",
        "Blue": "#2196F3",
        "Purple": "#9C27B0",
        "Green": "#4CAF50",
        "Orange": "#FF9800",
        "Red": "#F44336",
        "Deep Purple": "#432567",
        "White": "#FFFFFF",

        
        "Cyan": "#00BCD4",
        "Light Blue": "#03A9F4",
        "Indigo": "#3F51B5",
        "Pink": "#E91E63",
        "Amber": "#FFC107",
        "Lime": "#CDDC39",
        "Yellow": "#FFEB3B",
        "Deep Orange": "#FF5722",
        "Brown": "#795548",
        "Grey": "#9E9E9E",
        "Blue Grey": "#607D8B",
        "Black": "#000000"
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
        '''future
        self.accent_combo.currentIndexChanged.connect(
            self.preview_theme
        )
'''
        self.font_combo.currentIndexChanged.connect(
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
        ''' future
        index = self.accent_combo.findData(
            settings.accent
        )
'''
        #if index >= 0:
         #   self.accent_combo.setCurrentIndex(
          #      index
           # )
            
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
        #settings.accent = (
         #   self.accent_combo.currentData()
        #)
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

       # preview_settings.accent = (
        #    self.accent_combo.currentData()
        #)

        preview_settings.font_family = (
            self.font_combo.currentText()
        )

        preview_settings.font_size = (
            self.font_spin.value()
        )

        self.theme_manager.apply_theme(
            preview_settings
        )

    def cancel_settings(self):

        self.settings_manager.settings = deepcopy(
            self.original_settings
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
        ''' Not working currently(future feature)
        self.accent_combo = QComboBox()

        for name, colour in self.ACCENTS.items():

            self.accent_combo.addItem(
                name,
                colour
            )

        form_layout.addRow(
            "Accent:",
            self.accent_combo
        )'''
        self.font_combo = QComboBox()
        # ---------------------------------
        # Font family
        # ---------------------------------
        self.font_combo.setItemDelegate(
        FontDelegate(self.font_combo)
    )

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
    def preview_hovered_font(self, index):

        font_name = index.data()

        if not font_name:
            return

        preview_settings = deepcopy(
            self.settings_manager.settings
        )

        preview_settings.theme = (
            self.theme_combo.currentData()
        )

        preview_settings.font_family = (
            font_name
        )

        preview_settings.font_size = (
            self.font_spin.value()
        )

        self.theme_manager.apply_theme(
            preview_settings
        )

    def restore_font_preview(self):

        settings = self.settings_manager.settings

        self.theme_manager.apply_theme(
            settings
        )