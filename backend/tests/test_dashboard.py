"""Tests for the Dashboard aggregation endpoint."""
import datetime

import pytest
from httpx import AsyncClient

_TODAY = datetime.date.today().isoformat()


@pytest.mark.asyncio
async def test_dashboard_fresh_user_returns_zero_defaults(async_client: AsyncClient) -> None:
    """A brand-new user with no data gets zeros/nulls — never a 500."""
    resp = await async_client.get("/api/v1/dashboard/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["date"] == _TODAY
    assert data["integrity_score_today"] is None
    assert data["workout_streak"] == 0
    assert data["did_workout_today"] is False
    assert float(data["monthly_expense_total"]) == 0.0
    assert data["active_resolutions"] == 0
    assert data["completed_resolutions"] == 0
    assert data["small_wins_today"] == 0
    assert len(data["last_7_days_integrity"]) == 7
    assert all(v is None for v in data["last_7_days_integrity"])
    assert data["expense_summary_this_month"] == {}


@pytest.mark.asyncio
async def test_dashboard_with_full_data(async_client: AsyncClient) -> None:
    """Dashboard aggregates all feature data correctly."""
    # Seed a small win
    await async_client.post(
        "/api/v1/small-wins/",
        json={"date": _TODAY, "text": "Did a thing", "entry_type": "win"},
    )
    # Seed a completed task (also counts)
    await async_client.post(
        "/api/v1/small-wins/",
        json={"date": _TODAY, "text": "Future task", "entry_type": "task", "completed": True},
    )
    # Seed a pending task (should NOT count)
    await async_client.post(
        "/api/v1/small-wins/",
        json={"date": _TODAY, "text": "Pending task", "entry_type": "task", "completed": False},
    )
    # Seed workout
    await async_client.post(
        "/api/v1/workouts/",
        json={"date": _TODAY, "did_workout": True, "activity_type": "Run", "duration_mins": 30},
    )
    # Seed self assessment
    await async_client.post(
        "/api/v1/self-assessment/",
        json={"date": _TODAY, "performed_well_partner": True, "note": ""},
    )
    # Seed expense
    await async_client.post(
        "/api/v1/expenses/",
        json={"date": _TODAY, "amount": "50.00", "category": "Groceries"},
    )
    await async_client.post(
        "/api/v1/expenses/",
        json={"date": _TODAY, "amount": "20.00", "category": "Transport"},
    )
    # Seed resolution (active)
    r = await async_client.post(
        "/api/v1/resolutions/",
        json={"title": "Learn guitar"},
    )
    assert r.status_code == 201
    res_id = r.json()["id"]
    # Seed completed resolution
    r2 = await async_client.post(
        "/api/v1/resolutions/",
        json={"title": "Read 12 books"},
    )
    assert r2.status_code == 201
    await async_client.patch(
        f"/api/v1/resolutions/{r2.json()['id']}",
        json={"status": "completed"},
    )

    resp = await async_client.get("/api/v1/dashboard/")
    assert resp.status_code == 200
    data = resp.json()

    assert data["small_wins_today"] == 2  # win + completed task
    assert data["workout_streak"] == 1
    assert data["did_workout_today"] is True
    assert data["integrity_score_today"] == 100
    assert float(data["monthly_expense_total"]) == 70.0
    assert data["active_resolutions"] == 1
    assert data["completed_resolutions"] == 1
    assert float(data["expense_summary_this_month"]["Groceries"]) == 50.0
    assert float(data["expense_summary_this_month"]["Transport"]) == 20.0
    assert len(data["last_7_days_integrity"]) == 7
    # Today (last entry) should be 100
    assert data["last_7_days_integrity"][-1] == 100


@pytest.mark.asyncio
async def test_dashboard_partial_data(async_client: AsyncClient) -> None:
    """Partial data (only some features used) returns graceful nulls/zeros."""
    # Only log a workout — everything else empty
    await async_client.post(
        "/api/v1/workouts/",
        json={"date": _TODAY, "did_workout": True, "activity_type": "Bike", "duration_mins": 20},
    )

    resp = await async_client.get("/api/v1/dashboard/")
    assert resp.status_code == 200
    data = resp.json()

    assert data["integrity_score_today"] is None
    assert data["workout_streak"] == 1
    assert data["did_workout_today"] is True
    assert data["small_wins_today"] == 0
    assert float(data["monthly_expense_total"]) == 0.0
    assert data["active_resolutions"] == 0
