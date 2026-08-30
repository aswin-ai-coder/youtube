from kivymd.uix.navigationbar import (
    MDNavigationBar,
    MDNavigationItem,
    MDNavigationItemIcon,
    MDNavigationItemLabel,
)


class BottomNav(MDNavigationBar):
    """Material 3 navigation bar using KivyMD's native tab event."""

    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self._callback = callback
        self.bind(on_switch_tabs=self._on_switch_tabs)

        tabs = (
            ("home", "home", "Home"),
            ("queue", "download", "Queue"),
            ("history", "history", "History"),
            ("favorites", "heart", "Favorites"),
            ("settings", "cog", "Settings"),
        )

        for screen, icon, text in tabs:
            item = MDNavigationItem()
            item.screen = screen
            item.add_widget(MDNavigationItemIcon(icon=icon))
            item.add_widget(MDNavigationItemLabel(text=text))
            self.add_widget(item)

        self.set_active_item(self.children[-1])

    def _on_switch_tabs(self, _bar, item, _icon, _text):
        screen = getattr(item, "screen", None)
        if screen:
            self._callback(screen)
