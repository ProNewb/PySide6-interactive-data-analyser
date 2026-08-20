import json
from pathlib import Path

from core.app_settings import AppSettings


import json
from pathlib import Path

from core.app_settings import AppSettings


class SettingsManager:

    def __init__(self):

        self.settings_file = Path("settings.json")

        self.settings = AppSettings()

        self.load_settings()

    def load_settings(self):

        if not self.settings_file.exists():
            return

        try:

            with open(self.settings_file, "r") as file:
                saved_settings = json.load(file)

            if "theme" in saved_settings:
                self.settings.theme = saved_settings["theme"]

            if "font_size" in saved_settings:
                self.settings.font_size = saved_settings["font_size"]

            if "start_maximized" in saved_settings:
                self.settings.start_maximized = (
                    saved_settings["start_maximized"]
                )

        except (json.JSONDecodeError, OSError):
            pass

    def save_settings(self):

        data = {
            "theme": self.settings.theme,
            "accent": self.settings.accent,
            "font_family": self.settings.font_family,
            "font_size": self.settings.font_size,
            "start_maximized": self.settings.start_maximized
        }

        with open(self.settings_file, "w") as file:
            json.dump(data, file, indent=4)



    def get(self, key):

        return getattr(
            self.settings,
            key
        )

    def set(self, key, value):

        setattr(
            self.settings,
            key,
            value
        )