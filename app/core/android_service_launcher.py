from __future__ import annotations

from kivy.utils import platform


class AndroidServiceLauncher:
    """Start the python-for-android foreground downloader service safely."""

    def __init__(self) -> None:
        self.started = False

    def start(self) -> bool:
        if platform != "android":
            return False

        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            package_name = str(activity.getPackageName())
            service_class = autoclass(f"{package_name}.ServiceDownloader")
            service_class.start(activity, "")
            self.started = True
            return True
        except Exception:
            return False
