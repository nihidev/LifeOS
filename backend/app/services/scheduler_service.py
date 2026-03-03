import datetime
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.models.small_win import SmallWin
from app.services.email_service import send_small_wins_reminder

logger = logging.getLogger(__name__)


async def check_and_remind(session_factory: async_sessionmaker[AsyncSession]) -> None:
    if not settings.REMINDER_EMAIL:
        logger.debug("REMINDER_EMAIL not set, skipping reminder check")
        return

    today = datetime.date.today()
    try:
        async with session_factory() as db:
            result = await db.execute(
                select(SmallWin).where(SmallWin.date == today).limit(1)
            )
            has_wins = result.scalar_one_or_none() is not None

        if not has_wins:
            logger.info("No wins logged today — sending reminder to %s", settings.REMINDER_EMAIL)
            await send_small_wins_reminder(settings.REMINDER_EMAIL)
        else:
            logger.debug("Wins already logged today, skipping reminder")
    except Exception:
        logger.exception("Error in check_and_remind scheduler job")


def build_scheduler(session_factory: async_sessionmaker[AsyncSession]) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_and_remind,
        "cron",
        hour=20,
        minute=0,
        args=[session_factory],
    )
    return scheduler
