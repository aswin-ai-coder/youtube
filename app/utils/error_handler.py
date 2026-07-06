"""
Centralized error handling for the application.
"""

from __future__ import annotations

import traceback
from typing import Optional

from app.utils.logger import get_logger


logger = get_logger("errors")


class ErrorHandler:
    """Central place to log and format application errors."""

    @staticmethod
    def log(
        exception: Exception,
        *,
        context: str = "",
    ) -> None:
        """
        Log an exception together with its traceback.
        """

        if context:
            logger.error(f"{context}: {exception}")
        else:
            logger.error(str(exception))

        logger.error(traceback.format_exc())

    @staticmethod
    def user_message(
        exception: Exception,
        default: str = "An unexpected error occurred.",
    ) -> str:
        """
        Return a user-friendly error message.
        """

        message = str(exception).strip()

        return message if message else default

    @staticmethod
    def handle(
        exception: Exception,
        *,
        context: str = "",
        default: str = "An unexpected error occurred.",
    ) -> str:
        """
        Log the error and return a message suitable for the UI.
        """

        ErrorHandler.log(exception, context=context)

        return ErrorHandler.user_message(
            exception,
            default=default,
        )
