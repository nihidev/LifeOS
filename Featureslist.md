# LifeOS — Features List & Build Tracker

**Last Updated:** 2026-03-02
**Version:** 1.0

This file tracks the build status of every feature, sub-task, and component.
Update status as work progresses. This is the **source of truth** for what's done and what's next.

---

## Status Legend

| Symbol | Meaning |
|---|---|
| `[ ]` | Not started |
| `[~]` | In progress |
| `[x]` | Complete |
| `[!]` | Blocked |
| `[-]` | Deferred to v2 |

---

## Phase 0 — Project Bootstrap

The foundation everything else builds on. Must be 100% complete before any feature work.

### Monorepo Scaffold
- [ ] Create `lifeos/` root directory with `backend/` and `frontend/` subdirs
- [ ] Create root `.gitignore` (covers Python, Node, .env files, __pycache__, .next)
- [ ] Create root `README.md` with setup instructions
- [ ] Initialize git with `main` and `develop` branches
- [ ] Set up branch protection rules on `main`

### Backend Bootstrap
- [ ] Create `backend/` Python project structure (all dirs per Context.md)
- [ ] Set up `requirements.txt` with pinned versions:
  - fastapi==0.115.x
  - uvicorn[standard]
  - sqlalchemy[asyncio]==2.0.x
  - asyncpg
  - alembic
  - pydantic==2.x
  - pydantic-settings
  - python-jose[cryptography] (JWT)
  - httpx (for testing)
  - pytest
  - pytest-asyncio
  - pytest-cov
  - black
  - ruff
  - resend
  - apscheduler
- [ ] Create `app/core/config.py` (pydantic-settings with all env vars)
- [ ] Create `app/core/database.py` (async SQLAlchemy engine, AsyncSession factory)
- [ ] Create `app/core/security.py` (JWT validation against Supabase JWKS)
- [ ] Create `app/core/deps.py` (`get_db`, `get_current_user` dependencies)
- [ ] Create `app/main.py` (FastAPI app, lifespan, middleware, CORS, include routers)
- [ ] Create `app/api/v1/router.py` (master router)
- [ ] Create `backend/.env.example`
- [ ] Create `backend/Dockerfile`
- [ ] Set up Alembic: `alembic init alembic`
- [ ] Configure `alembic/env.py` to use async engine + load models
- [ ] Create `backend/tests/conftest.py` with test DB fixture and mock user
- [ ] Verify: `uvicorn app.main:app --reload` starts without errors
- [ ] Verify: `GET /health` returns `{ "status": "ok" }`

### Frontend Bootstrap
- [ ] Initialize Next.js 14: `npx create-next-app@latest frontend --typescript --tailwind --app`
- [ ] Install dependencies:
  - `@supabase/supabase-js`
  - `@tanstack/react-query`
  - `zustand`
  - `shadcn/ui` (init: `npx shadcn-ui@latest init`)
  - `date-fns`
  - `lucide-react`
  - `recharts` (for dashboard charts)
- [ ] Create `lib/api.ts` (base fetch wrapper with auth header injection)
- [ ] Create `lib/auth.ts` (Supabase client, session helpers)
- [ ] Create `lib/utils.ts` (cn(), formatDate(), formatCurrency())
- [ ] Create root `app/layout.tsx` (QueryClientProvider, font, metadata)
- [ ] Create `app/page.tsx` (redirect to dashboard or login)
- [ ] Create `(auth)/login/page.tsx` (magic link form)
- [ ] Create `(auth)/callback/page.tsx` (Supabase OAuth callback handler)
- [ ] Create sidebar layout with navigation links to all features
- [ ] Create `components/layout/Sidebar.tsx`
- [ ] Create `components/layout/Header.tsx`
- [ ] Create `components/layout/PageWrapper.tsx`
- [ ] Create `frontend/.env.local.example`
- [ ] Verify: `npm run dev` starts without errors
- [ ] Verify: Login page renders at `localhost:3000/login`

### GitHub Actions CI
- [ ] Create `.github/workflows/backend.yml` (on push: black check, ruff, pytest)
- [ ] Create `.github/workflows/frontend.yml` (on push: eslint, type-check, next build)

---

## Phase 1 — Small Wins

**Sprint Goal:** Users can log, edit, delete daily wins. Email reminder if none logged.

### Backend
- [ ] Create `app/models/small_win.py` (SQLAlchemy model)
- [ ] Generate Alembic migration for `small_wins` table
- [ ] Apply migration: `alembic upgrade head`
- [ ] Create `app/schemas/small_win.py` (SmallWinCreate, SmallWinUpdate, SmallWinResponse)
- [ ] Create `app/repositories/small_win_repository.py`
  - [ ] `create(user_id, data) → SmallWin`
  - [ ] `get_by_date(user_id, date) → list[SmallWin]`
  - [ ] `get_by_id(user_id, id) → SmallWin | None`
  - [ ] `update(user_id, id, data) → SmallWin`
  - [ ] `delete(user_id, id) → bool`
- [ ] Create `app/services/small_win_service.py`
  - [ ] Validate text length
  - [ ] Raise 404 if win not found
  - [ ] Raise 403 if win belongs to other user
- [ ] Create `app/api/v1/small_wins.py` (4 endpoints, all auth-protected)
- [ ] Register router in `app/api/v1/router.py`
- [ ] Write `tests/test_small_wins.py`:
  - [ ] Test: create win → 201, correct response shape
  - [ ] Test: get wins by date → returns list
  - [ ] Test: edit win → text updated
  - [ ] Test: delete win → 200, gone from DB
  - [ ] Test: get other user's win → 403
  - [ ] Test: edit other user's win → 403
  - [ ] Test: create with empty text → 422
  - [ ] Test: unauthenticated → 401

### Frontend
- [ ] Create `hooks/useSmallWins.ts` (React Query hooks: useSmallWins, useCreateWin, useUpdateWin, useDeleteWin)
- [ ] Create `components/features/small-wins/SmallWinCard.tsx` (single win display with edit/delete)
- [ ] Create `components/features/small-wins/SmallWinForm.tsx` (text input + submit)
- [ ] Create `app/(dashboard)/small-wins/page.tsx` (date picker, list, form, empty state)
- [ ] Write tests:
  - [ ] Test: SmallWinCard renders text
  - [ ] Test: edit button opens inline edit
  - [ ] Test: delete triggers mutation
  - [ ] Test: SmallWinForm submits correctly
  - [ ] Test: page shows empty state when no wins

### Email Reminder
- [ ] Create `app/services/email_service.py` (Resend wrapper, send_small_wins_reminder())
- [ ] Create `app/services/scheduler_service.py` (APScheduler setup, register daily job)
- [ ] Register scheduler in `app/main.py` lifespan
- [ ] Write test:
  - [ ] Test: no entry today → email would be sent (mock Resend)
  - [ ] Test: entry exists today → no email sent

---

## Phase 2 — Workout Tracking

**Sprint Goal:** Log workouts, view streak, monthly summary.

### Backend
- [ ] Create `app/models/workout.py`
- [ ] Generate + apply Alembic migration
- [ ] Create `app/schemas/workout.py` (WorkoutCreate, WorkoutResponse, StreakResponse, MonthlySummaryResponse)
- [ ] Create `app/repositories/workout_repository.py`
  - [ ] `upsert(user_id, date, data) → Workout` (creates or replaces)
  - [ ] `get_by_date(user_id, date) → Workout | None`
  - [ ] `get_range(user_id, from_date, to_date) → list[Workout]`
  - [ ] `get_monthly(user_id, year, month) → list[Workout]`
- [ ] Create `app/services/workout_service.py`
  - [ ] `calculate_streak(user_id) → StreakResponse`
  - [ ] `get_monthly_summary(user_id, year, month) → MonthlySummaryResponse`
- [ ] Create `app/api/v1/workouts.py` (3 endpoints)
- [ ] Write `tests/test_workouts.py`:
  - [ ] Test: post workout → upsert behavior (second POST same date overwrites)
  - [ ] Test: streak calculation with gap → resets to 0
  - [ ] Test: streak calculation continuous → correct count
  - [ ] Test: monthly summary counts correct
  - [ ] Test: no duplicate per day

### Frontend
- [ ] Create `hooks/useWorkout.ts`
- [ ] Create `components/features/workout/WorkoutToggle.tsx` (did_workout yes/no + activity input)
- [ ] Create `components/features/workout/StreakDisplay.tsx` (flame icon + count)
- [ ] Create `components/features/workout/MonthlyCalendar.tsx` (month grid, green/grey/none days)
- [ ] Create `app/(dashboard)/workout/page.tsx`
- [ ] Write tests:
  - [ ] Test: StreakDisplay shows correct number
  - [ ] Test: WorkoutToggle submits correctly

---

## Phase 3 — Self Assessment

**Sprint Goal:** Daily integrity check, score history, rolling average.

### Backend
- [ ] Create `app/models/self_assessment.py`
- [ ] Generate + apply Alembic migration
- [ ] Create `app/schemas/self_assessment.py`
- [ ] Create `app/repositories/self_assessment_repository.py`
  - [ ] `upsert(user_id, date, data) → SelfAssessment`
  - [ ] `get_by_date(user_id, date) → SelfAssessment | None`
  - [ ] `get_history(user_id, limit, offset) → list[SelfAssessment]`
  - [ ] `get_average_score(user_id, days) → float`
- [ ] Create `app/services/self_assessment_service.py`
  - [ ] Score calculation logic (binary for v1)
  - [ ] History with average
- [ ] Create `app/api/v1/self_assessment.py` (3 endpoints)
- [ ] Write `tests/test_self_assessment.py`:
  - [ ] Test: performed_well=true → score=100
  - [ ] Test: performed_well=false → score=0
  - [ ] Test: second POST same day overwrites
  - [ ] Test: history paginates correctly
  - [ ] Test: average score calculated correctly

### Frontend
- [ ] Create `hooks/useSelfAssessment.ts`
- [ ] Create `components/features/self-assessment/AssessmentForm.tsx` (yes/no toggle + note)
- [ ] Create `components/features/self-assessment/ScoreHistory.tsx` (line chart, 30-day view)
- [ ] Create `app/(dashboard)/self-assessment/page.tsx`
- [ ] Write tests:
  - [ ] Test: form renders question text
  - [ ] Test: submit updates score display
  - [ ] Test: ScoreHistory renders chart

---

## Phase 4 — Expenses

**Sprint Goal:** Log expenses, view monthly breakdown, category totals.

### Backend
- [ ] Create `app/models/expense.py`
- [ ] Generate + apply Alembic migration
- [ ] Create `app/schemas/expense.py`
- [ ] Create `app/repositories/expense_repository.py`
  - [ ] `create(user_id, data) → Expense`
  - [ ] `get_by_month(user_id, year, month) → list[Expense]`
  - [ ] `get_summary(user_id, year, month) → CategorySummary`
  - [ ] `delete(user_id, id) → bool`
- [ ] Create `app/services/expense_service.py`
  - [ ] Validate positive amount
  - [ ] Aggregate by category
- [ ] Create `app/api/v1/expenses.py` (4 endpoints)
- [ ] Write `tests/test_expenses.py`:
  - [ ] Test: create expense → stored correctly
  - [ ] Test: negative amount → 422
  - [ ] Test: zero amount → 422
  - [ ] Test: monthly list filters by month correctly
  - [ ] Test: summary aggregation correct across categories
  - [ ] Test: delete own expense → gone
  - [ ] Test: delete other user's expense → 403

### Frontend
- [ ] Create `hooks/useExpenses.ts`
- [ ] Create `components/features/expenses/ExpenseForm.tsx` (amount, category autocomplete, note)
- [ ] Create `components/features/expenses/ExpenseList.tsx` (grouped by date)
- [ ] Create `components/features/expenses/CategoryChart.tsx` (pie/bar chart via Recharts)
- [ ] Create `app/(dashboard)/expenses/page.tsx` (month selector, form, list, chart)
- [ ] Write tests:
  - [ ] Test: ExpenseForm validates amount
  - [ ] Test: CategoryChart renders with data
  - [ ] Test: monthly total displays correctly

---

## Phase 5 — Resolutions

**Sprint Goal:** Create goals, track status and progress, view on dashboard.

### Backend
- [ ] Create `app/models/resolution.py`
- [ ] Generate + apply Alembic migration
- [ ] Create `app/schemas/resolution.py`
- [ ] Create `app/repositories/resolution_repository.py`
  - [ ] `create(user_id, data) → Resolution`
  - [ ] `get_all(user_id, status?) → list[Resolution]`
  - [ ] `update(user_id, id, data) → Resolution`
- [ ] Create `app/services/resolution_service.py`
  - [ ] Enforce status transitions
  - [ ] Auto-set progress=100 when completed
- [ ] Create `app/api/v1/resolutions.py` (3 endpoints)
- [ ] Write `tests/test_resolutions.py`:
  - [ ] Test: create resolution → defaults correct
  - [ ] Test: progress > 100 → 422
  - [ ] Test: progress < 0 → 422
  - [ ] Test: complete sets progress to 100
  - [ ] Test: filter by status works

### Frontend
- [ ] Create `hooks/useResolutions.ts`
- [ ] Create `components/features/resolutions/ResolutionCard.tsx` (progress bar, status badge)
- [ ] Create `components/features/resolutions/ResolutionForm.tsx`
- [ ] Create `app/(dashboard)/resolutions/page.tsx`
- [ ] Write tests:
  - [ ] Test: progress bar renders at correct width
  - [ ] Test: status badge shows correct color
  - [ ] Test: form creates resolution

---

## Phase 6 — Dashboard Aggregation

**Sprint Goal:** Single-call dashboard with all today's metrics.

### Backend
- [ ] Create `app/services/dashboard_service.py`
  - [ ] Calls all feature repositories
  - [ ] Assembles `DashboardResponse`
  - [ ] Handles case where any feature has no data for today (nulls, not errors)
- [ ] Create `app/schemas/dashboard.py` (DashboardResponse with all fields)
- [ ] Create `app/api/v1/dashboard.py` (single GET endpoint)
- [ ] Write `tests/test_dashboard.py`:
  - [ ] Test: fresh user → all fields null/zero (no 500)
  - [ ] Test: data for all features → correct aggregation
  - [ ] Test: partial data → graceful null handling

### Frontend
- [ ] Create `hooks/useDashboard.ts`
- [ ] Create `components/features/dashboard/IntegrityScoreCard.tsx`
- [ ] Create `components/features/dashboard/WorkoutStreakCard.tsx`
- [ ] Create `components/features/dashboard/ExpenseSummaryCard.tsx`
- [ ] Create `components/features/dashboard/ResolutionProgressCard.tsx`
- [ ] Create `components/features/dashboard/Last7DaysChart.tsx` (integrity trend)
- [ ] Update `app/(dashboard)/page.tsx` to use dashboard data
- [ ] Write tests:
  - [ ] Test: dashboard renders all cards
  - [ ] Test: null/zero data renders without crash

---

## Phase 7 — Email Reminder Hardening

**Sprint Goal:** Reliable, tested email system with configurable timing.

- [ ] Finalize `email_service.py` with proper error handling (Resend failures don't crash app)
- [ ] Add user preference for reminder time (hardcoded 8 PM for v1 — just make it a config)
- [ ] Add idempotency check (don't send twice if cron runs twice)
- [ ] Integration test with mock Resend API
- [ ] Manual test: trigger via `POST /api/v1/admin/trigger-reminder` (dev-only endpoint)

---

## Phase 8 — Secondary Features

### Food Logs
- [ ] Backend: model, migration, repo, service, routes
- [ ] Backend: tests
- [ ] Frontend: form, list, page, hooks, tests

### Grocery List
- [ ] Backend: model, migration, repo, service, routes
- [ ] Backend: tests (check/uncheck, clear checked items)
- [ ] Frontend: checklist component, page, hooks, tests

### Appointments
- [ ] Backend: model, migration, repo, service, routes
- [ ] Backend: tests
- [ ] Frontend: calendar/list view, form, page, hooks, tests

---

## Phase 9 — CI/CD & Productionization

- [ ] Finalize `backend.yml` GitHub Actions workflow
- [ ] Finalize `frontend.yml` GitHub Actions workflow
- [ ] Ensure `pytest --cov` reports ≥ 85% coverage
- [ ] Ensure `next build` passes with zero errors
- [ ] Add `docker-compose.yml` for local full-stack dev
- [ ] Add `Makefile` with common commands (test, lint, migrate, dev)
- [ ] Document deploy instructions in `README.md`

---

## Deferred to v2

- [ ] Google Calendar OAuth integration
- [ ] Apple Calendar ICS sync
- [ ] Multi-user / accountability partners
- [ ] Weekly email digest
- [ ] CSV/PDF export
- [ ] Dark mode
- [ ] Mobile PWA
- [ ] Expanded integrity score (multiple questions)

---

## Coverage Tracker

| Feature | BE Tests | BE Coverage | FE Tests | Status |
|---|---|---|---|---|
| Phase 0 (Bootstrap) | — | — | — | `[ ]` |
| Small Wins | `[ ]` | — | `[ ]` | `[ ]` |
| Workout Tracking | `[ ]` | — | `[ ]` | `[ ]` |
| Self Assessment | `[ ]` | — | `[ ]` | `[ ]` |
| Expenses | `[ ]` | — | `[ ]` | `[ ]` |
| Resolutions | `[ ]` | — | `[ ]` | `[ ]` |
| Dashboard | `[ ]` | — | `[ ]` | `[ ]` |
| Email Reminder | `[ ]` | — | — | `[ ]` |
| Food Logs | `[ ]` | — | `[ ]` | `[ ]` |
| Grocery List | `[ ]` | — | `[ ]` | `[ ]` |
| Appointments | `[ ]` | — | `[ ]` | `[ ]` |
| **TOTAL** | | **Target: ≥85%** | | |
