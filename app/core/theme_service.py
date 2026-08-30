from __future__ import annotations

from app.core.settings_service import SettingsService


class ThemeService:
    """Persist and safely apply the KivyMD theme configuration."""

    _PALETTES = {
        "Red", "Pink", "Purple", "DeepPurple", "Indigo", "Blue",
        "LightBlue", "Cyan", "Teal", "Green", "LightGreen", "Lime",
        "Yellow", "Amber", "Orange", "DeepOrange", "Brown", "Gray",
        "BlueGray",
    }

    def __init__(self):
        self.settings = SettingsService()

    def current(self) -> str:
        value = str(self.settings.get("theme", "dark")).strip().lower()
        return "light" if value == "light" else "dark"

    def save(self, theme: str) -> None:
        normalized = "light" if str(theme).strip().lower() == "light" else "dark"
        self.settings.set("theme", normalized)
        self.settings.save()

    def palette(self) -> str:
        value = self.settings.get("accent_palette", "Blue")
        return str(value) if str(value) in self._PALETTES else "Blue"

    def save_palette(self, palette: str) -> None:
        normalized = str(palette)
        if normalized not in self._PALETTES:
            normalized = "Blue"
        self.settings.set("accent_palette", normalized)
        self.settings.save()

    def apply(self, app) -> None:
        app.theme_cls.theme_style = "Light" if self.current() == "light" else "Dark"
        app.theme_cls.primary_palette = self.palette()
