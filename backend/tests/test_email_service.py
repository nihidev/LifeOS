"""Tests for the email service and scheduler reminder logic."""
import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.email_service import send_small_wins_reminder
from app.services.scheduler_service import check_and_remind, reset_idempotency


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_factory(has_wins: bool) -> MagicMock:
    """Build a mock async session factory that returns or doesn't return a SmallWin."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = MagicMock() if has_wins else None

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=False)

    return MagicMock(return_value=mock_db)


# ---------------------------------------------------------------------------
# 1. No wins today → email is sent
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_wins_today_triggers_email() -> None:
    reset_idempotency()
    with (
        patch("app.services.scheduler_service.settings") as mock_settings,
        patch(
            "app.services.scheduler_service.send_small_wins_reminder",
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_reminder,
    ):
        mock_settings.REMINDER_EMAIL = "user@example.com"
        result = await check_and_remind(_make_factory(has_wins=False))
        mock_reminder.assert_called_once_with("user@example.com")
        assert result == "sent"


# ---------------------------------------------------------------------------
# 2. Wins exist today → email is NOT sent
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_wins_exist_today_skips_email() -> None:
    reset_idempotency()
    with (
        patch("app.services.scheduler_service.settings") as mock_settings,
        patch(
            "app.services.scheduler_service.send_small_wins_reminder",
            new_callable=AsyncMock,
        ) as mock_reminder,
    ):
        mock_settings.REMINDER_EMAIL = "user@example.com"
        result = await check_and_remind(_make_factory(has_wins=True))
        mock_reminder.assert_not_called()
        assert result == "skipped_has_wins"


# ---------------------------------------------------------------------------
# 3. Idempotency — calling twice on same day only sends once
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_idempotency_only_sends_once_per_day() -> None:
    reset_idempotency()
    with (
        patch("app.services.scheduler_service.settings") as mock_settings,
        patch(
            "app.services.scheduler_service.send_small_wins_reminder",
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_reminder,
    ):
        mock_settings.REMINDER_EMAIL = "user@example.com"
        factory = _make_factory(has_wins=False)

        first = await check_and_remind(factory)
        second = await check_and_remind(factory)

        assert first == "sent"
        assert second == "skipped_already_sent"
        mock_reminder.assert_called_once()


# ---------------------------------------------------------------------------
# 4. REMINDER_EMAIL not set → silently skips
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_reminder_email_skips_silently() -> None:
    reset_idempotency()
    with patch("app.services.scheduler_service.settings") as mock_settings:
        mock_settings.REMINDER_EMAIL = ""
        result = await check_and_remind(_make_factory(has_wins=False))
        assert result == "skipped_no_email"


# ---------------------------------------------------------------------------
# 5. Resend failure doesn't raise — returns False, doesn't crash app
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resend_failure_does_not_crash() -> None:
    with patch("app.services.email_service.resend.Emails.send", side_effect=Exception("network error")):
        result = await send_small_wins_reminder("user@example.com")
        assert result is False


# ---------------------------------------------------------------------------
# 6. Resend is called with correct payload
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resend_called_with_correct_payload() -> None:
    with patch("app.services.email_service.resend.Emails.send") as mock_send:
        with patch("app.services.email_service.settings") as mock_settings:
            mock_settings.RESEND_API_KEY = "re_test"
            result = await send_small_wins_reminder("user@example.com")

        call_args = mock_send.call_args[0][0]
        assert call_args["to"] == ["user@example.com"]
        assert "small wins" in call_args["subject"].lower()
        assert result is True
