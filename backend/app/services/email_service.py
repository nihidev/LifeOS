import asyncio
import logging

import resend

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_small_wins_reminder(to_email: str) -> bool:
    """Send the daily small-wins reminder. Returns True if sent, False on failure."""
    try:
        resend.api_key = settings.RESEND_API_KEY
        await asyncio.to_thread(
            resend.Emails.send,
            {
                "from": "LifeOS <noreply@lifeos.app>",
                "to": [to_email],
                "subject": "Don't forget to log your small wins today!",
                "html": (
                    "<p>Hey! You haven't logged any small wins today.</p>"
                    "<p>Take a moment to reflect on what you accomplished — "
                    "every win counts.</p>"
                ),
            },
        )
        logger.info("Reminder sent to %s", to_email)
        return True
    except Exception:
        logger.exception("Failed to send small wins reminder to %s", to_email)
        return False
