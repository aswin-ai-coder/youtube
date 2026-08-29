from kivy.metrics import dp
from kivy.app import App
from app.core.theme_service import ThemeService
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.button import MDButton, MDButtonText

from app.core.settings_service import SettingsService


class SettingsScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = SettingsService()
        self.theme = ThemeService()
        scroll = MDScrollView()

        root = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(20),
            padding=dp(20),
        )

        root.add_widget(
            MDLabel(
                text="Settings",
                bold=True,
                adaptive_height=True,
            )
        )

        root.add_widget(
            MDLabel(
                text="Download Folder",
                adaptive_height=True,
            )
        )

        self.folder = MDTextField(
            text=self.settings.get("download_folder"),
        )
        root.add_widget(self.folder)

        root.add_widget(
            MDLabel(
                text="Filename Template",
                adaptive_height=True,
            )
        )

        self.template = MDTextField(
            text=self.settings.get("filename_template"),
        )
        root.add_widget(self.template)

        root.add_widget(
            MDLabel(
                text="Clipboard Monitor",
                adaptive_height=True,
            )
        )

        self.clipboard = MDSwitch(
            active=self.settings.get("clipboard_monitor", True)
        )
        root.add_widget(self.clipboard)

        root.add_widget(
            MDLabel(
                text="Notifications",
                adaptive_height=True,
            )
        )

        self.notify = MDSwitch(
            active=self.settings.get("notifications", True)
        )
        root.add_widget(self.notify)

        save = MDButton(
            style="filled",
            size_hint_y=None,
            height=dp(52),
        )
        save.add_widget(MDButtonText(text="SAVE SETTINGS"))
        save.bind(on_release=self.save_settings)

        root.add_widget(MDLabel(text="Theme", adaptive_height=True))

        light = MDButton(style="outlined")
        light.add_widget(MDButtonText(text="Light Theme"))
        light.bind(on_release=lambda x: self.change_theme("Light"))
        root.add_widget(light)

        dark = MDButton(style="outlined")
        dark.add_widget(MDButtonText(text="Dark Theme"))
        dark.bind(on_release=lambda x: self.change_theme("Dark"))
        root.add_widget(dark)

        root.add_widget(MDLabel(text="Accent Color", adaptive_height=True))

        for color in ("Blue", "Green", "Red", "Orange", "Purple"):
            button = MDButton(style="outlined")
            button.add_widget(MDButtonText(text=color))
            button.bind(on_release=lambda x, c=color: self.change_color(c))
            root.add_widget(button)

        root.add_widget(save)
        scroll.add_widget(root)
        self.add_widget(scroll)

    def save_settings(self, *_):
        self.settings.set("download_folder", self.folder.text)
        self.settings.set("filename_template", self.template.text)
        self.settings.set("clipboard_monitor", self.clipboard.active)
        self.settings.set("notifications", self.notify.active)
        self.settings.save()
        print("Settings Saved")

    def change_theme(self, theme):
        app = App.get_running_app()
        self.theme.save(theme)
        app.theme_cls.theme_style = theme

    def change_color(self, color):
        app = App.get_running_app()
        app.theme_cls.primary_palette = color
        self.theme.settings.set("primary_color", color)
        self.theme.settings.save()
