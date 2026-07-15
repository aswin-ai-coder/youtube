from plyer import notification


class NotificationService:

    @staticmethod
    def show(title, message):

        try:

            notification.notify(
                title=title,
                message=message,
                timeout=5,
            )

        except Exception:

            pass
