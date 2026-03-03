# LifeOS — Build Progress

**Last Updated:** 2026-03-03
**Current Phase:** Phase 4 (Expenses) ✅ COMPLETE. Next: Phase 5 (Resolutions).

---

## Phase 0 — Bootstrap ✅ COMPLETE

### Step 1 — Scaffold ✅
- Monorepo directories, `.gitignore`, `README.md`, `develop` branch

### Step 2 — Backend Bootstrap ✅
- FastAPI app, CORS, `/health`, JWT middleware, `get_db()`, `config.py`, `security.py`, `deps.py`

### Step 3 — Alembic Setup ✅
- `alembic.ini`, async `env.py`, `script.py.mako`

### Step 4 — Frontend Bootstrap ✅
- Next.js 16 App Router, Tailwind v4, shadcn/ui, TanStack Query, `lib/api.ts`, `lib/auth.ts`, auth pages, sidebar, dashboard layout

### Step 5 — CI Setup ✅
- `.github/workflows/backend.yml` + `frontend.yml`

---

## Phase 1 — Small Wins ✅ COMPLETE + E2E VERIFIED

### Backend
- Model, schemas, repository, service, routes, migration 001
- Tests: 16/16 passing (incl. task creation + toggle)

### Frontend
- `types/small-win.ts`, `hooks/useSmallWins.ts`, `SmallWinForm.tsx`, `SmallWinList.tsx`, `small-wins/page.tsx`

### E2E Verified ✅
- Log win/task, edit, delete, date navigation, win count, future date task planning

---

## Phase 2 — Workout Tracking ✅ COMPLETE + E2E VERIFIED

### Backend
- Model, schemas, repository, service, routes, migration 002
- Tests: 16/16 passing (incl. multi-entry, delete, monthly dedup)

### Frontend
- `types/workout.ts`, `hooks/useWorkout.ts`, `WorkoutForm.tsx`, `StreakCard.tsx`, `MonthlyCalendar.tsx`, `workout/page.tsx`

### E2E Verified ✅
- Multi-entry per day, delete entries, streak, monthly summary, duration on calendar

---

## Phase 3 — Self Assessment ✅ COMPLETE + E2E VERIFIED

### Backend
- Model, schemas, repository, service, routes, migration 003
- Tests: 12/12 passing

### Frontend
- `types/self-assessment.ts`, `hooks/useSelfAssessment.ts`, `AssessmentForm.tsx`, `ScoreHistory.tsx`, `self-assessment/page.tsx`

### E2E Verified ✅
- Yes/No toggle, required note on No, history chart

---

## Post-Phase Enhancements ✅ (commit 09c2b3c, 2026-03-03)

### Small Wins — Tasks feature
- Migration 004: `entry_type TEXT DEFAULT 'win'`, `completed BOOLEAN NULL`
- Dual-mode form: Log Win (today/past) | Log Task (future dates: task-only)
- Trophy icon (amber) for wins + completed tasks; Square icon for incomplete tasks
- Clicking icon toggles task completion
- Win count = wins + completed tasks only (pending tasks excluded)
- Future date navigation enabled for task pre-planning

### Workout — Multi-entry per day
- Migration 005: dropped `uq_workouts_user_date` unique constraint
- `GET /workouts/` returns `list[WorkoutResponse]`; `DELETE /workouts/{id}` added
- `upsert()` replaced by `create()` (always inserts)
- "Yes, I worked out" button opens detail form (no auto-submit); "Rest day" submits immediately
- Entries list with delete buttons shown below form
- Streak + monthly summary aggregate by date (`any did_workout=true` per day)
- MonthlyCalendar shows accumulated duration (mins) per workout day
- Next-day navigation disabled (workouts: current/past only)

### Self Assessment — Required note on No
- Save disabled + red hint shown when No selected with empty note

### Bug Fixes
- **Timezone bug**: `shiftDate()` in all 3 pages rewritten to use `Date.UTC()` — was broken for UTC+ timezones (right arrow did nothing)

---

## Phases 4–9 Status

| Phase | Feature | Status |
|---|---|---|
| 4 | Expenses | Not started |
| 5 | Resolutions | Not started |
| 6 | Dashboard Aggregation | Not started |
| 7 | Email Reminder Hardening | Not started |
| 8 | Secondary Features (Food, Grocery, Appointments) | Not started |
| 9 | CI/CD & Productionization | Not started |

---

## Git Workflow (from this point forward)
- All features developed on `feat/<name>` branches
- PR opened via `gh pr create`, reviewed, merged to `main`
- No direct commits to `main` for new features

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
