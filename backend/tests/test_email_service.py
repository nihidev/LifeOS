"""Tests for the email service and scheduler reminder logic."""
import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.email_service import send_small_wins_reminder
from app.services.scheduler_service import check_and_remind


# ---------------------------------------------------------------------------
# 1. No wins today → email is sent
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_wins_today_triggers_email() -> None:
    today = datetime.date.today()

    # Build a mock session factory whose session returns no wins
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=False)

    mock_factory = MagicMock(return_value=mock_db)

    with (
        patch("app.services.scheduler_service.settings") as mock_settings,
        patch("app.services.email_service.resend.Emails.send") as mock_send,
    ):
        mock_settings.REMINDER_EMAIL = "user@example.com"
        mock_settings.RESEND_API_KEY = "test-key"
        # Patch the send inside scheduler module path
        with patch(
            "app.services.scheduler_service.send_small_wins_reminder",
            new_callable=AsyncMock,
        ) as mock_reminder:
            await check_and_remind(mock_factory)
            mock_reminder.assert_called_once_with("user@example.com")


# ---------------------------------------------------------------------------
# 2. Wins exist today → email is NOT sent
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_wins_exist_today_skips_email() -> None:
    from app.models.small_win import SmallWin

    mock_win = MagicMock(spec=SmallWin)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_win

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=False)

    mock_factory = MagicMock(return_value=mock_db)

    with (
        patch("app.services.scheduler_service.settings") as mock_settings,
        patch(
            "app.services.scheduler_service.send_small_wins_reminder",
            new_callable=AsyncMock,
        ) as mock_reminder,
    ):
        mock_settings.REMINDER_EMAIL = "user@example.com"
        await check_and_remind(mock_factory)
        mock_reminder.assert_not_called()
