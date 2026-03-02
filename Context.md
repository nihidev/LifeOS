# LifeOS — Project Context

## What This Is

LifeOS is a **personal discipline and accountability dashboard** — a structured self-tracking web app for one primary user (the developer) that measures discipline, integrity, financial awareness, physical consistency, and long-term goal tracking. It is **not** a public SaaS product in v1.

---

## Purpose of This Document

This file is the **entry point** for any Claude Code agent working on this project. Read this before touching any code.

It answers:
- What is being built and why
- The exact tech stack and why each piece was chosen
- How the codebase is structured
- What the build order is
- How to think about this project as an engineer

For full feature specs, see `PRD.md`.
For the feature list and sprint status, see `Featureslist.md`.
For agent orchestration strategy, see `Agents.md`.
For sub-agent task assignments, see `SubAgents.md`.

---

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Frontend | Next.js 14 (App Router) | SSR, file-based routing, React ecosystem |
| Styling | Tailwind CSS + shadcn/ui | Fast, composable UI primitives |
| Backend | FastAPI (Python 3.12) | Async-first, strict typing via Pydantic v2, fast |
| Auth | Supabase Auth (JWT) | Managed auth, works with FastAPI middleware |
| Database | Supabase Postgres | Managed Postgres, RLS built in |
| ORM | SQLAlchemy 2.0 (async) | Async support, type-safe models |
| Migrations | Alembic | Industry standard with SQLAlchemy |
| Email | Resend API | Simple transactional email, great DX |
| Scheduler | APScheduler | Lightweight in-process cron for daily reminders |
| Testing (BE) | pytest + httpx + pytest-asyncio | Async test support |
| Testing (FE) | Jest + React Testing Library | Component and integration tests |
| Linting (BE) | Black + Ruff | Fast, opinionated formatting |
| Linting (FE) | ESLint + Prettier | Standard Next.js toolchain |
| CI/CD | GitHub Actions | Free, monorepo-friendly |
| Containerization | Docker (backend only for now) | Predictable backend deploys |

---

## Monorepo Structure

```
lifeos/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry, middleware, lifespan
│   │   ├── core/
│   │   │   ├── config.py        # pydantic-settings env config
│   │   │   ├── database.py      # Async SQLAlchemy engine + session
│   │   │   ├── security.py      # JWT validation, Supabase token verify
│   │   │   └── deps.py          # FastAPI dependency injection (get_db, get_user)
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py    # Master router that includes all feature routers
│   │   │       ├── small_wins.py
│   │   │       ├── workouts.py
│   │   │       ├── self_assessment.py
│   │   │       ├── expenses.py
│   │   │       ├── resolutions.py
│   │   │       ├── food_logs.py
│   │   │       ├── grocery.py
│   │   │       ├── appointments.py
│   │   │       └── dashboard.py
│   │   ├── models/              # SQLAlchemy ORM models (one file per table)
│   │   ├── schemas/             # Pydantic v2 request/response DTOs
│   │   ├── services/            # Business logic (no DB queries in routes)
│   │   ├── repositories/        # DB access layer (repository pattern)
│   │   └── tests/
│   │       ├── conftest.py      # Fixtures: test DB, test client, mock user
│   │       └── test_*.py        # One test file per feature
│   ├── alembic/                 # Migration scripts
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── app/                     # Next.js App Router
│   │   ├── layout.tsx           # Root layout, font, providers
│   │   ├── page.tsx             # Dashboard home
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── callback/page.tsx
│   │   └── (dashboard)/
│   │       ├── small-wins/page.tsx
│   │       ├── workout/page.tsx
│   │       ├── self-assessment/page.tsx
│   │       ├── expenses/page.tsx
│   │       ├── resolutions/page.tsx
│   │       ├── food/page.tsx
│   │       ├── grocery/page.tsx
│   │       └── appointments/page.tsx
│   ├── components/
│   │   ├── ui/                  # shadcn/ui primitives (do not edit manually)
│   │   ├── layout/              # Sidebar, Header, PageWrapper
│   │   └── features/            # Feature-specific components
│   ├── lib/
│   │   ├── api.ts               # Typed API client (fetch wrapper)
│   │   ├── auth.ts              # Supabase client-side auth helpers
│   │   └── utils.ts             # cn(), date helpers, formatters
│   ├── hooks/                   # Custom React hooks (useSmallWins, useWorkout, etc.)
│   ├── store/                   # Zustand global state (minimal — prefer server state)
│   ├── tests/
│   └── package.json
│
├── .github/
│   └── workflows/
│       ├── backend.yml          # pytest + black + ruff on push
│       └── frontend.yml         # jest + eslint + next build on push
│
├── PRD.md
├── Context.md
├── Featureslist.md
├── Agents.md
└── SubAgents.md
```

---

## Engineering Standards (Non-Negotiable)

These must be followed on every file written:

### Backend
1. **No business logic in route handlers.** Routes call services. Services call repositories.
2. **Pydantic v2 for all DTOs.** `model_config = ConfigDict(from_attributes=True)`.
3. **Repository pattern.** One repository class per model. No raw SQL in services.
4. **Async everywhere.** `async def` for all route handlers and DB calls. Use `AsyncSession`.
5. **Dependency injection.** `get_db` and `get_current_user` must be FastAPI `Depends()`.
6. **Config via pydantic-settings.** No hardcoded strings. All secrets in `.env`.
7. **Structured logging.** Use Python `logging` with JSON output in prod.
8. **API versioning.** All routes under `/api/v1/`.
9. **Auth on every protected route.** Every endpoint (except health) requires `get_current_user`.

### Frontend
1. **Server Components by default.** Only use `"use client"` when absolutely necessary.
2. **Typed API calls.** The `lib/api.ts` client must be fully typed with request/response types.
3. **No `any` types.** TypeScript strict mode is on.
4. **shadcn/ui for all UI primitives.** Do not write custom Button/Input/Modal from scratch.
5. **React Query (TanStack Query) for all server state.** No `useEffect` for fetching.
6. **Zustand only for true global UI state** (e.g., sidebar open/close). Not for server data.
7. **Route-level code splitting** is automatic with App Router — do not add manual lazy loading unless profiling shows it's needed.

---

## Auth Flow

1. User visits app → redirected to `/login` if no session.
2. Login via Supabase Auth (email magic link or OAuth, v1 = magic link only).
3. Supabase issues a JWT. Stored in `localStorage` / `httpOnly cookie` via Supabase client.
4. Frontend sends `Authorization: Bearer <jwt>` on every API call.
5. FastAPI middleware validates JWT against Supabase JWKS endpoint.
6. `get_current_user` dep extracts `user_id` (UUID) from token — used for all DB queries.
7. **All DB queries must be scoped by `user_id`.** This is the row-level security guarantee at the application layer (Supabase RLS also enabled as a backup).

---

## Environment Variables

### Backend `.env`
```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWT_SECRET=
DATABASE_URL=postgresql+asyncpg://...
RESEND_API_KEY=
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend `.env.local`
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Build Order (Sprint Map)

Always build in this order. Do NOT skip phases.

| Phase | What Gets Built | Depends On |
|---|---|---|
| 0 | Monorepo scaffold, env config, DB connection, auth middleware | Nothing |
| 1 | Small Wins (full stack: model → repo → service → route → frontend page) | Phase 0 |
| 2 | Workout Tracking + streak logic | Phase 0 |
| 3 | Self Assessment + integrity score | Phase 0 |
| 4 | Expenses + category analytics | Phase 0 |
| 5 | Resolutions | Phase 0 |
| 6 | Dashboard aggregation API | Phases 1–5 |
| 7 | Email reminder system (APScheduler + Resend) | Phase 1 |
| 8 | Food Logs, Grocery List, Appointments | Phase 0 |
| 9 | CI/CD, Dockerfile, GitHub Actions | All phases |

---

## What "Done" Means for Each Feature

A feature is **not done** until:
- [ ] SQLAlchemy model created and Alembic migration generated + applied
- [ ] Pydantic schemas (request + response) written
- [ ] Repository class with all CRUD methods
- [ ] Service class with business logic
- [ ] FastAPI router with all endpoints
- [ ] All endpoints auth-protected
- [ ] Backend unit tests passing (85%+ coverage)
- [ ] Frontend page/component built
- [ ] Frontend API hook written (React Query)
- [ ] Frontend component tests written
- [ ] ESLint + Black pass with zero warnings

---

## Key Design Decisions

1. **FastAPI over Django/Flask**: Async-native, Pydantic-native, fastest for API-only backends.
2. **Supabase Auth over custom JWT**: Eliminates auth implementation risk, built-in email magic link.
3. **Repository pattern**: Makes unit testing trivial — mock the repository, test the service.
4. **React Query over Redux/Zustand for server state**: Caching, invalidation, loading/error states for free.
5. **App Router over Pages Router**: Future-proof, streaming, server components, layouts.
6. **shadcn/ui over other libraries**: Accessible, customizable, not opinionated about styling system.

---

## Local Development Setup

```bash
# Clone and enter
cd lifeos

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in .env
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd ../frontend
npm install
cp .env.local.example .env.local
# Fill in .env.local
npm run dev
```

Backend runs on `http://localhost:8000`
Frontend runs on `http://localhost:3000`
API docs at `http://localhost:8000/docs`
