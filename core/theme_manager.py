from qt_material import apply_stylesheet


class ThemeManager:

    def __init__(self, application):

        self.application = application

    def apply_theme(self, settings):

        # ------------------------------
        # Material base theme
        # ------------------------------

        apply_stylesheet(
            self.application,
            theme=settings.theme
        )

        # ------------------------------
        # User customisation
        # ------------------------------

        custom_style = f"""
            QWidget {{
                font-family: "{settings.font_family}";
                font-size: {settings.font_size}pt;
            }}
        """

        self.application.setStyleSheet(
            self.application.styleSheet()
            + custom_style
        )