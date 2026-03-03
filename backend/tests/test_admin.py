"""Tests for the admin trigger-reminder endpoint."""
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_trigger_reminder_dev_environment(async_client: AsyncClient) -> None:
    """In development, the trigger endpoint calls check_and_remind and returns result."""
    with (
        patch("app.api.v1.admin.settings") as mock_settings,
        patch(
            "app.api.v1.admin.check_and_remind",
            new_callable=AsyncMock,
            return_value="sent",
        ) as mock_check,
    ):
        mock_settings.ENVIRONMENT = "development"
        resp = await async_client.post("/api/v1/admin/trigger-reminder")
        assert resp.status_code == 200
        assert resp.json() == {"result": "sent"}
        mock_check.assert_called_once()


@pytest.mark.asyncio
async def test_trigger_reminder_production_returns_404(async_client: AsyncClient) -> None:
    """In production, the trigger endpoint returns 404."""
    with patch("app.api.v1.admin.settings") as mock_settings:
        mock_settings.ENVIRONMENT = "production"
        resp = await async_client.post("/api/v1/admin/trigger-reminder")
        assert resp.status_code == 404
