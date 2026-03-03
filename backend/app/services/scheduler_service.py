import datetime
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.models.small_win import SmallWin
from app.services.email_service import send_small_wins_reminder

logger = logging.getLogger(__name__)

# Idempotency: track the last date a reminder was successfully sent.
# In-memory is sufficient — single-user personal app, process restarts are rare.
_last_sent_date: datetime.date | None = None


async def check_and_remind(session_factory: async_sessionmaker[AsyncSession]) -> str:
    """
    Check whether a small-wins reminder is needed and send it if so.

    Returns one of: "sent" | "skipped_already_sent" | "skipped_has_wins" | "skipped_no_email"
    """
    global _last_sent_date

    if not settings.REMINDER_EMAIL:
        logger.debug("REMINDER_EMAIL not set, skipping reminder check")
        return "skipped_no_email"

    today = datetime.date.today()

    # Idempotency: don't send twice on the same day
    if _last_sent_date == today:
        logger.debug("Reminder already sent today (%s), skipping", today)
        return "skipped_already_sent"

    try:
        async with session_factory() as db:
            result = await db.execute(
                select(SmallWin).where(SmallWin.date == today).limit(1)
            )
            has_wins = result.scalar_one_or_none() is not None

        if has_wins:
            logger.debug("Wins already logged today, skipping reminder")
            return "skipped_has_wins"

        logger.info("No wins logged today — sending reminder to %s", settings.REMINDER_EMAIL)
        sent = await send_small_wins_reminder(settings.REMINDER_EMAIL)
        if sent:
            _last_sent_date = today
        return "sent" if sent else "skipped_has_wins"

    except Exception:
        logger.exception("Error in check_and_remind scheduler job")
        return "skipped_has_wins"


def reset_idempotency() -> None:
    """Reset the in-memory sent-date tracker. Used in tests."""
    global _last_sent_date
    _last_sent_date = None


def build_scheduler(session_factory: async_sessionmaker[AsyncSession]) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_and_remind,
        "cron",
        hour=settings.REMINDER_HOUR,
        minute=0,
        args=[session_factory],
    )
    return scheduler
