# LifeOS — Build Progress

**Last Updated:** 2026-03-04
**Current Phase:** Phase 9 (CI/CD & Productionization) — in progress.

---

## Phase 0 — Bootstrap ✅ COMPLETE
- Monorepo, `.gitignore`, FastAPI app, CORS, `/health`, JWT middleware, `get_db()`, `config.py`, `security.py`, `deps.py`
- Alembic async setup, Next.js 16 App Router, Tailwind v4, shadcn/ui, TanStack Query
- CI: `.github/workflows/backend.yml` + `frontend.yml`

---

## Phase 1 — Small Wins ✅ COMPLETE + E2E VERIFIED
- Backend: model, schemas, repo, service, routes, migration 001 — 16/16 tests
- Frontend: `types/small-win.ts`, `hooks/useSmallWins.ts`, `SmallWinForm.tsx`, `SmallWinList.tsx`, `small-wins/page.tsx`
- E2E: log win/task, edit, delete, date nav, win count, future task planning

---

## Phase 2 — Workout Tracking ✅ COMPLETE + E2E VERIFIED
- Backend: model, schemas, repo, service, routes, migration 002 — 16/16 tests
- Frontend: `types/workout.ts`, `hooks/useWorkout.ts`, `WorkoutForm.tsx`, `StreakCard.tsx`, `MonthlyCalendar.tsx`, `workout/page.tsx`
- E2E: multi-entry per day, delete, streak, monthly summary, duration on calendar

---

## Phase 3 — Self Assessment ✅ COMPLETE + E2E VERIFIED
- Backend: model, schemas, repo, service, routes, migration 003 — 12/12 tests
- Frontend: `types/self-assessment.ts`, `hooks/useSelfAssessment.ts`, `AssessmentForm.tsx`, `ScoreHistory.tsx`, `self-assessment/page.tsx`
- E2E: Yes/No toggle, required note on No, history chart

---

## Post-Phase Enhancements ✅ (2026-03-03)

### Small Wins — Tasks feature
- Migration 004: `entry_type TEXT DEFAULT 'win'`, `completed BOOLEAN NULL`
- Dual-mode form: Log Win (today/past) | Log Task (future dates: task-only)
- Trophy icon (amber) for wins + completed tasks; Square icon for incomplete tasks
- Win count = wins + completed tasks only (pending tasks excluded)

### Workout — Multi-entry per day
- Migration 005: dropped `uq_workouts_user_date` unique constraint
- Always inserts; `DELETE /workouts/{id}` added; streak aggregates by date

### Self Assessment — Required note on No
### Bug Fix — `shiftDate()` rewritten to use `Date.UTC()` (UTC+ timezone fix)

---

## Phase 4 — Expenses ✅ COMPLETE + E2E VERIFIED
- Backend: model, schemas, repo, service, routes, migration 006 — tests passing
- Frontend: `types/expense.ts`, `hooks/useExpenses.ts`, form, list, monthly chart, `expenses/page.tsx`
- Categories validated server-side: Groceries, Transport, Social Life, Fitness, Lifestyle, Bills, Self-improvement

---

## Phase 5 — Resolutions ✅ COMPLETE + E2E VERIFIED
- Backend: `resolutions`, `resolution_check_ins`, `resolution_ai_cache` — migration 007 — 12/12 tests
- CRUD: POST, GET (status filter), PATCH, DELETE (cascade); monthly check-in upsert
- Auto-advances `not_started` → `in_progress` on first check-in; auto-sets `progress_percent=100` on complete
- OpenAI integration: GPT-4o-mini signal analysis with daily DB cache + graceful fallback
- Frontend: `ResolutionForm`, `ResolutionCard`, `MonthHeatmap`, `CheckInModal`, `AIAnalysisCard`, filter strip

---

## Phase 6 — Dashboard Aggregation ✅ COMPLETE (merged PR #3)
- Backend: `GET /api/v1/dashboard/` — single endpoint, `DashboardResponse`, `dashboard_service.py` — 3/3 tests
- Frontend: `useDashboard`, `IntegrityScoreCard`, `WorkoutStreakCard`, `ExpenseSummaryCard`, `ResolutionProgressCard`, `Last7DaysChart` (recharts), skeleton loading
- Graceful null/zero for fresh users

---

## Phase 7 — Email Reminder Hardening ✅ COMPLETE (merged PR #4)
- `config.py`: added `REMINDER_HOUR: int = 20` (override via env var)
- `email_service.py`: `resend.Emails.send` wrapped in `asyncio.to_thread()`; returns `bool`
- `scheduler_service.py`: in-memory idempotency (`_last_sent_date`); status return strings; uses `REMINDER_HOUR`
- `admin.py`: `POST /api/v1/admin/trigger-reminder` — dev-only, 404 in production
- 8 tests: sent, skipped_has_wins, idempotency, no_email, Resend failure isolation, payload validation, dev/prod guard

---

## Phase 8 — Secondary Features ✅ COMPLETE (merged PR #5)
- Food Logs: model, migration 008, repo, service, routes, tests
- Water Intake: model, migration 008, repo, service, routes, tests
- Grocery List: model, migration 009, repo, service, routes, tests
- **Appointments: removed from scope permanently**
- Frontend: food log form/list, water intake tracker, grocery checklist, hooks, pages

## Deployment ✅ COMPLETE (2026-03-04)
- Backend live on Render (Docker): https://lifeos-api-qk86.onrender.com
- DATABASE_URL: Supabase transaction pooler `aws-1-eu-central-1.pooler.supabase.com:6543`
- Frontend live on Vercel: https://lifeos-nine-pi.vercel.app

## Phase 9 — CI/CD & Productionization 🔄 IN PROGRESS

### Code Fixes (pre-PR)
| Task | File | Status |
|---|---|---|
| Fix `dashboard.py` to use `DB`/`CurrentUser` aliases (not raw `Depends()`) | `api/v1/dashboard.py:14-18` | ✅ Done |
| Add `user_id` filter to scheduler's SmallWin query | `services/scheduler_service.py:41` | N/A — single-user app, no user context in scheduler |
| Fix silent error catch in FoodLogForm, ResolutionForm, ExpenseForm (show toast) | frontend forms | ✅ Done |
| Disable form inputs during mutation in ExpenseForm | `ExpenseForm` | ✅ Done |

### Backend CI/CD
| Task | Status |
|---|---|
| Add `--cov-fail-under=85` to `backend.yml` | ✅ Done |
| Add post-deploy smoke test (`curl /health`) to CI | Not started |
| Verify `pytest --cov` actually hits ≥ 85% locally | ✅ Done — **96%** (was 75% due to SQLAlchemy greenlet tracer bug; fixed with `concurrency=["greenlet"]` in pyproject.toml) |
| Consolidate duplicate test fixtures into `tests/conftest.py` | Not started |

### Dockerfile Hardening
| Task | Status |
|---|---|
| Add non-root user (`RUN useradd -m appuser` + `USER appuser`) | ✅ Done |
| Add `HEALTHCHECK` instruction | ✅ Done |
| Create `.dockerignore` to exclude `.venv`, `__pycache__`, `.git`, etc. | ✅ Done |

### Frontend CI/CD
| Task | Status |
|---|---|
| Tighten CORS: whitelist methods `["GET","POST","PATCH","DELETE","OPTIONS"]` and headers `["Content-Type","Authorization"]` | ✅ Done |
| Verify `next build` passes with zero errors | Not started |

### Frontend Tests (biggest chunk)
| Task | Status |
|---|---|
| Hook tests: `useSmallWins`, `useWorkout`, `useExpenses`, `useResolutions`, `useFoodLogs`, `useGrocery`, `useSelfAssessment` | Not started |
| Component tests: `SmallWinForm`, `SmallWinList`, `ExpenseForm`, `WorkoutForm`, `ResolutionForm` | Not started |
| Aim for ≥ 80% frontend coverage | Not started |

### Infrastructure Files
| Task | Status |
|---|---|
| `docker-compose.yml` for local Postgres + backend dev | Not started |
| `Makefile` with `make test`, `make lint`, `make run`, `make migrate` | Not started |
| Expand `README.md` with quick-start, deploy instructions, architecture | Not started |

---

## Key Decisions & Lessons

- **uv** for all Python ops (`uv venv`, `uv pip install`, `uv run`)
- `resend==2.23.0` (2.5.0 doesn't exist on PyPI)
- **Next.js 16** uses `proxy.ts` not `middleware.ts`
- **SQLAlchemy `get_db()`** must `await session.commit()` after yield; `flush()` alone does not persist
- **Supabase JWT** is ES256 (ECC P-256) — validate via JWKS endpoint, not HS256 shared secret
- **`shiftDate()`** must use `Date.UTC()` arithmetic — local time + `toISOString()` breaks in UTC+ timezones
- **SmallWinUpdate.text** is optional (enables PATCH with only `completed` field for checkbox toggle)
- **Checkbox** shadcn component must be installed separately: `npx shadcn@latest add checkbox`
- **Skeleton** shadcn component must be installed separately: `npx shadcn@latest add skeleton`
- **Expense category** validated server-side — must be one of the 7 predefined categories
- **feat/* branches always rebased on main before merging** — router.py conflicts common when multiple phases add routes simultaneously
- **SQLAlchemy async coverage**: add `[tool.coverage.run] concurrency = ["greenlet"]` to `pyproject.toml` — without it, coverage.py loses its tracer inside `await db.execute()` (SQLAlchemy uses greenlet internally), making async services appear at ~33% coverage even when fully tested. Fixed: 75% → 96%.
