from app.core.settings_service import SettingsService


class ThemeService:

    def __init__(self):

        self.settings = SettingsService()

    def current(self):

        return self.settings.get(
            "theme",
            "Dark",
        )

    def save(self, theme):

        self.settings.set(
            "theme",
            theme,
        )

    def apply(self, app):

        theme = self.current()

        app.theme_cls.theme_style = theme

        app.theme_cls.primary_palette = self.settings.get(
            "primary_color",
            "Blue",
        )
