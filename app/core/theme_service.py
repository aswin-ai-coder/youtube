from __future__ import annotations

from app.core.settings_service import SettingsService


class ThemeService:
    """Persist and safely apply the KivyMD theme configuration."""

    def __init__(self):
        self.settings = SettingsService()

    def current(self) -> str:
        value = self.settings.get("theme", "Dark")
        return "Light" if str(value).strip().lower() == "light" else "Dark"

    def save(self, theme: str) -> None:
        normalized = "Light" if str(theme).strip().lower() == "light" else "Dark"
        self.settings.set("theme", normalized)
        self.settings.save()

    def apply(self, app) -> None:
        app.theme_cls.theme_style = self.current()
        palette = self.settings.get("accent_color") or self.settings.get("primary_color") or "Blue"
        allowed = {
            "Red", "Pink", "Purple", "DeepPurple", "Indigo", "Blue",
            "LightBlue", "Cyan", "Teal", "Green", "LightGreen", "Lime",
            "Yellow", "Amber", "Orange", "DeepOrange", "Brown", "Gray",
            "BlueGray",
        }
        palette = str(palette)
        app.theme_cls.primary_palette = palette if palette in allowed else "Blue"
