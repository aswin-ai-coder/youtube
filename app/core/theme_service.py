from app.core.settings_service import SettingsService


class ThemeService:
    """Persist and safely apply the KivyMD theme configuration."""

    def __init__(self):
        self.settings = SettingsService()

    def current(self):
        value = self.settings.get("theme", "Dark")
        return "Light" if str(value).strip().lower() == "light" else "Dark"

    def save(self, theme):
        normalized = "Light" if str(theme).strip().lower() == "light" else "Dark"
        self.settings.set("theme", normalized)
        self.settings.save()

    def apply(self, app):
        app.theme_cls.theme_style = self.current()
        palette = self.settings.get("primary_color", "Blue")
        allowed = {
            "Red", "Pink", "Purple", "DeepPurple", "Indigo", "Blue",
            "LightBlue", "Cyan", "Teal", "Green", "LightGreen", "Lime",
            "Yellow", "Amber", "Orange", "DeepOrange", "Brown", "Gray",
            "BlueGray",
        }
        app.theme_cls.primary_palette = palette if palette in allowed else "Blue"
