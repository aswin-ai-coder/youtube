from kivymd.uix.navigationbar import (
    MDNavigationBar,
    MDNavigationItem,
    MDNavigationItemIcon,
    MDNavigationItemLabel,
)


class BottomNav(MDNavigationBar):

    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)

        tabs = [
            ("home", "home", "Home"),
            ("queue", "download", "Queue"),
            ("history", "history", "History"),
            ("favorites", "heart", "Favorites"),
            ("settings", "cog", "Settings"),
        ]

        for screen, icon, text in tabs:

            item = MDNavigationItem()

            item.screen = screen

            item.add_widget(
                MDNavigationItemIcon(
                    icon=icon,
                )
            )

            item.add_widget(
                MDNavigationItemLabel(
                    text=text,
                )
            )

            item.bind(
                on_release=lambda x, s=screen: callback(s)
            )

            self.add_widget(item)
