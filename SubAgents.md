# LifeOS — Sub-Agent Specifications

**For:** Claude Code (Orchestrator spawning sub-agents via Task tool)
**Version:** 1.0

This document contains the **exact prompt templates** for each type of sub-agent. When spawning a sub-agent, copy the relevant template and fill in the `{{VARIABLES}}` with specific values.

Each template is self-contained — a sub-agent receiving it should be able to complete its task without needing to ask questions.

---

## Sub-Agent Index

| Agent Type | When to Use |
|---|---|
| [ScaffoldAgent](#scaffoldagent) | Phase 0: Create monorepo directory structure |
| [BackendBootstrapAgent](#backendbootstrapagent) | Phase 0: Set up FastAPI skeleton + core modules |
| [AlembicSetupAgent](#alembicsetupage) | Phase 0: Initialize Alembic with async config |
| [FrontendBootstrapAgent](#frontendbootstrapagent) | Phase 0: Initialize Next.js + install deps + base layout |
| [CISetupAgent](#cisetupage) | Phase 0/9: Create GitHub Actions workflows |
| [ModelMigrationAgent](#modelmigrationagent) | Per-feature: Create SQLAlchemy model + Alembic migration |
| [BackendFeatureAgent](#backendfeatureagent) | Per-feature: Schema + Repo + Service + Router |
| [BackendTestAgent](#backendtestagent) | Per-feature: pytest unit tests |
| [FrontendFeatureAgent](#frontendfeaturedagent) | Per-feature: Hooks + Components + Page |
| [FrontendTestAgent](#frontendtestagent) | Per-feature: Jest + RTL tests |
| [DashboardBackendAgent](#dashboardbackendagent) | Phase 6: Dashboard aggregation service |
| [DashboardFrontendAgent](#dashboardfrontendagent) | Phase 6: Dashboard UI components |
| [EmailReminderAgent](#emailreminderagent) | Phase 1/7: APScheduler + Resend integration |
| [FixAgent](#fixagent) | Error recovery: Fix broken code from another agent |

---

## ScaffoldAgent

**Purpose:** Create the monorepo directory structure and git setup.

**Prompt Template:**
```
You are building the LifeOS monorepo scaffold. Read /Users/dev/LifeOS/Context.md first to understand the project structure.

Your job is to create the exact directory and file structure described in the "Monorepo Structure" section of Context.md.

Tasks:
1. Create all directories listed in the monorepo structure (use `mkdir -p`)
2. Create placeholder files (empty __init__.py, .gitkeep) where needed to preserve directory structure in git
3. Create the root `.gitignore` covering: __pycache__, .venv, *.pyc, .env, .env.local, node_modules, .next, dist, .DS_Store, *.egg-info, .pytest_cache, .coverage, coverage/, htmlcov/
4. Create the root `README.md` with: project name, one-line description, links to Context.md and PRD.md, and "See Context.md for setup instructions."
5. Run `git init` and create initial commit with message "chore: initialize monorepo structure"
6. Create `develop` branch: `git checkout -b develop`

Do NOT create any application code — only structure.
Do NOT create .env files (user must fill these in).
Do create .env.example files with all keys listed but values empty.

Working directory: /Users/dev/LifeOS
```

---

## BackendBootstrapAgent

**Purpose:** Create the complete FastAPI skeleton with all core modules.

**Prompt Template:**
```
You are building the LifeOS FastAPI backend skeleton.

First read these files in order:
1. /Users/dev/LifeOS/Context.md (engineering standards, env vars, tech stack)
2. /Users/dev/LifeOS/PRD.md (auth flow section)

Your job: Create the backend core modules. Do NOT create any feature code yet.

Files to create:

1. backend/requirements.txt
   Pin these exact packages:
   fastapi==0.115.5
   uvicorn[standard]==0.32.1
   sqlalchemy[asyncio]==2.0.36
   asyncpg==0.30.0
   alembic==1.14.0
   pydantic==2.10.3
   pydantic-settings==2.6.1
   python-jose[cryptography]==3.3.0
   httpx==0.27.2
   pytest==8.3.4
   pytest-asyncio==0.24.0
   pytest-cov==6.0.0
   black==24.10.0
   ruff==0.8.3
   resend==2.5.0
   apscheduler==3.10.4

2. backend/app/__init__.py (empty)

3. backend/app/core/config.py
   - Use pydantic-settings BaseSettings
   - Fields: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET, DATABASE_URL, RESEND_API_KEY, ENVIRONMENT (default "development"), LOG_LEVEL (default "INFO"), CORS_ORIGINS (list, default ["http://localhost:3000"])
   - Singleton pattern: settings = Settings()

4. backend/app/core/database.py
   - Async SQLAlchemy engine using asyncpg
   - AsyncSession factory
   - Base = declarative_base()
   - get_db() async generator for dependency injection

5. backend/app/core/security.py
   - validate_token(token: str) -> dict
   - Uses python-jose to decode JWT
   - Validates against SUPABASE_JWT_SECRET from config
   - Raises HTTPException(401) on invalid token
   - Returns decoded payload dict

6. backend/app/core/deps.py
   - get_db: yields AsyncSession (uses database.py)
   - get_current_user: extracts Bearer token, calls security.validate_token(), returns user_id as UUID
   - CurrentUser = Annotated[UUID, Depends(get_current_user)]
   - DB = Annotated[AsyncSession, Depends(get_db)]

7. backend/app/main.py
   - FastAPI app with title="LifeOS API", version="1.0.0"
   - CORS middleware: allow origins from config.CORS_ORIGINS, allow credentials, allow all methods/headers
   - Include api/v1/router at prefix="/api/v1"
   - Lifespan context manager (placeholder for scheduler)
   - GET /health → { "status": "ok", "environment": config.ENVIRONMENT }

8. backend/app/api/__init__.py (empty)
9. backend/app/api/v1/__init__.py (empty)
10. backend/app/api/v1/router.py
    - APIRouter()
    - Comment placeholders for each feature router (will be added later)

11. backend/app/models/__init__.py (empty)
12. backend/app/schemas/__init__.py (empty)
13. backend/app/services/__init__.py (empty)
14. backend/app/repositories/__init__.py (empty)

15. backend/tests/__init__.py (empty)
16. backend/tests/conftest.py
    - Fixture: test AsyncSession using SQLite in-memory (asyncpg won't work in tests, use aiosqlite)
    - Fixture: mock_user_id = UUID (fixed value)
    - Fixture: test FastAPI TestClient with get_current_user overridden to return mock_user_id
    - Fixture: async_client using httpx AsyncClient

17. backend/.env.example (all keys, empty values)
18. backend/pyproject.toml with [tool.black], [tool.ruff], [tool.pytest.ini_options] sections
    - pytest asyncio_mode = "auto"
    - black line-length = 88
    - ruff select = ["E", "F", "W"]

Verify at the end: `cd backend && uvicorn app.main:app --reload` runs and GET /health returns 200.

Engineering standards to follow (from Context.md):
- Async everywhere (async def, AsyncSession)
- No hardcoded strings
- Pydantic v2 syntax
- Type hints on all function signatures
```

---

## AlembicSetupAgent

**Purpose:** Initialize Alembic for async SQLAlchemy migrations.

**Prompt Template:**
```
You are setting up Alembic for the LifeOS FastAPI backend.

First read: /Users/dev/LifeOS/backend/app/core/database.py and /Users/dev/LifeOS/backend/app/core/config.py

Your job:
1. Run `cd /Users/dev/LifeOS/backend && alembic init alembic`
2. Modify `alembic/env.py` to:
   - Import the Base from app.core.database
   - Import config from app.core.config to get DATABASE_URL
   - Use `run_async_migrations()` pattern for async SQLAlchemy
   - Set target_metadata = Base.metadata
   - Load the DATABASE_URL from settings (not from alembic.ini)
3. Update `alembic.ini`:
   - Set sqlalchemy.url to empty string (it's loaded programmatically)
4. Create `alembic/versions/` directory with .gitkeep

The async migration pattern in env.py:
```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.core.database import Base
from app.core.config import settings
# import all models here so they are registered with Base.metadata
# from app.models import *  # uncomment as models are added

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

Verify: `cd /Users/dev/LifeOS/backend && alembic current` runs without error.
```

---

## FrontendBootstrapAgent

**Purpose:** Initialize the Next.js frontend with all dependencies and base layout.

**Prompt Template:**
```
You are setting up the LifeOS Next.js frontend.

First read: /Users/dev/LifeOS/Context.md (frontend section, monorepo structure)

Your job:

1. Initialize Next.js 14 in /Users/dev/LifeOS/frontend/:
   - TypeScript: yes
   - Tailwind: yes
   - App Router: yes
   - src/ directory: no
   - import alias: @/*

2. Install additional dependencies:
   npm install @supabase/supabase-js @tanstack/react-query zustand date-fns lucide-react recharts
   npm install -D @types/node

3. Initialize shadcn/ui:
   npx shadcn-ui@latest init
   (choose: Default style, Slate base color, CSS variables: yes)

   Add these components:
   npx shadcn-ui@latest add button card input label textarea badge progress toast dialog

4. Create frontend/lib/utils.ts:
   - cn() function using clsx + tailwind-merge
   - formatDate(date: Date | string, format?: string): string using date-fns
   - formatCurrency(amount: number, currency?: string): string (default USD)
   - getToday(): string (returns today as YYYY-MM-DD string)

5. Create frontend/lib/api.ts:
   - Base URL from NEXT_PUBLIC_API_URL env var
   - apiClient with methods: get<T>, post<T>, patch<T>, delete<T>
   - Each method: injects Authorization header from Supabase session
   - Throws ApiError with { message, status } on non-2xx
   - Full TypeScript generics

6. Create frontend/lib/auth.ts:
   - Create Supabase client (from @supabase/supabase-js)
   - signInWithMagicLink(email: string): Promise<void>
   - signOut(): Promise<void>
   - getSession(): Promise<Session | null>
   - getCurrentUserId(): Promise<string | null>

7. Create frontend/lib/queryClient.ts:
   - QueryClient instance with defaults: staleTime 5min, retry 1

8. Create frontend/app/layout.tsx:
   - Root layout with QueryClientProvider + Hydration boundary
   - Inter font
   - Correct metadata (title: "LifeOS", description: "Personal discipline dashboard")

9. Create frontend/app/page.tsx:
   - Server component
   - Check Supabase session server-side
   - If authenticated: redirect to /dashboard
   - If not: redirect to /login

10. Create frontend/app/(auth)/login/page.tsx:
    - "use client"
    - Magic link form (email input + send button)
    - Shows success message after send
    - Uses lib/auth.ts

11. Create frontend/app/(auth)/callback/page.tsx:
    - Handles Supabase OAuth callback
    - Exchanges code for session
    - Redirects to /dashboard

12. Create frontend/components/layout/Sidebar.tsx:
    - Navigation links to all features:
      / (Dashboard), /small-wins, /workout, /self-assessment, /expenses, /resolutions, /food, /grocery, /appointments
    - Icons from lucide-react
    - Highlight active route

13. Create frontend/components/layout/Header.tsx:
    - Shows current page title
    - Shows today's date
    - Sign out button

14. Create frontend/components/layout/PageWrapper.tsx:
    - Wraps page content with consistent padding
    - Accepts title prop

15. Create frontend/app/(dashboard)/layout.tsx:
    - Protected layout: redirects to /login if no session
    - Renders Sidebar + Header + children

16. Create frontend/app/(dashboard)/page.tsx:
    - Placeholder dashboard (we'll fill this in Phase 6)
    - Shows "Dashboard - Coming Soon" for now

17. Create frontend/.env.local.example:
    NEXT_PUBLIC_SUPABASE_URL=
    NEXT_PUBLIC_SUPABASE_ANON_KEY=
    NEXT_PUBLIC_API_URL=http://localhost:8000

18. Update frontend/tsconfig.json: ensure strict mode is true

19. Create frontend/jest.config.ts and frontend/jest.setup.ts for React Testing Library

Verify: `cd frontend && npm run build` passes with zero type errors.
```

---

## CISetupAgent

**Purpose:** Create GitHub Actions CI workflows.

**Prompt Template:**
```
You are creating GitHub Actions CI workflows for the LifeOS monorepo.

First read: /Users/dev/LifeOS/Context.md (CI/CD section)

Create these two workflow files:

1. /Users/dev/LifeOS/.github/workflows/backend.yml
   - Trigger: push and pull_request to main and develop
   - Paths filter: backend/**
   - Jobs (run in parallel where possible):
     a. lint: black --check backend/app && ruff check backend/app
     b. test: pytest backend/ --cov=app --cov-report=term-missing --cov-fail-under=85
   - Python version: 3.12
   - Use pip cache
   - Set env vars for test: SUPABASE_JWT_SECRET=test_secret, DATABASE_URL=sqlite+aiosqlite:///./test.db, etc.

2. /Users/dev/LifeOS/.github/workflows/frontend.yml
   - Trigger: push and pull_request to main and develop
   - Paths filter: frontend/**
   - Jobs (run in parallel where possible):
     a. lint: npm run lint (ESLint)
     b. typecheck: npx tsc --noEmit
     c. test: npm run test -- --coverage --watchAll=false
     d. build: npm run build
   - Node version: 20
   - Use npm cache

Both workflows should:
- Have a clear job name and step names
- Fail fast on errors
- Report coverage in PR comments (optional, use codecov action if available)
```

---

## ModelMigrationAgent

**Purpose:** Create one SQLAlchemy model and its Alembic migration.

**Prompt Template:**
```
You are creating the SQLAlchemy model and Alembic migration for the {{FEATURE_NAME}} feature of LifeOS.

First read these files:
1. /Users/dev/LifeOS/PRD.md (find the "{{FEATURE_NAME}}" section for the exact DB schema)
2. /Users/dev/LifeOS/backend/app/core/database.py (for Base and import patterns)
3. /Users/dev/LifeOS/backend/app/models/ (read any existing models for patterns)

Tasks:
1. Create /Users/dev/LifeOS/backend/app/models/{{MODEL_FILE}}.py
   - Use the exact column names, types, and constraints from PRD.md
   - Use SQLAlchemy 2.0 mapped_column() syntax (not Column())
   - Use Mapped[] type hints
   - Add __tablename__ = "{{TABLE_NAME}}"
   - Add created_at with server_default=func.now()
   - Add updated_at with server_default=func.now(), onupdate=func.now() (if table has it)
   - Import and extend Base from app.core.database

2. Update /Users/dev/LifeOS/backend/alembic/env.py:
   - Add import: from app.models.{{MODEL_FILE}} import {{ModelClass}}
   (This ensures the model is registered with Base.metadata for autogenerate)

3. Generate the migration:
   cd /Users/dev/LifeOS/backend
   alembic revision --autogenerate -m "add {{TABLE_NAME}} table"

4. Review the generated migration file — verify it matches the PRD.md schema exactly.
   If any column or constraint is missing, edit the migration file manually.

5. Apply the migration (for local dev db):
   alembic upgrade head

6. Verify: alembic current shows the migration as applied.

IMPORTANT: Use SQLAlchemy 2.0 syntax. Example:
```python
from sqlalchemy import String, Boolean, Date, Integer, Numeric, Text, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
import uuid
from datetime import date, datetime

class SmallWin(Base):
    __tablename__ = "small_wins"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
```

Variables to fill in before spawning:
- {{FEATURE_NAME}}: e.g., "Small Wins", "Workout Tracking"
- {{MODEL_FILE}}: e.g., "small_win", "workout"
- {{TABLE_NAME}}: e.g., "small_wins", "workouts"
- {{ModelClass}}: e.g., "SmallWin", "Workout"
```

---

## BackendFeatureAgent

**Purpose:** Create schemas, repository, service, and route for one feature.

**Prompt Template:**
```
You are implementing the backend for the {{FEATURE_NAME}} feature of LifeOS.

First read these files in order:
1. /Users/dev/LifeOS/PRD.md — find the "{{FEATURE_NAME}}" section. Follow it exactly.
2. /Users/dev/LifeOS/Context.md — engineering standards (service layer, repo pattern, etc.)
3. /Users/dev/LifeOS/backend/app/models/{{MODEL_FILE}}.py — the existing model
4. /Users/dev/LifeOS/backend/app/core/deps.py — for CurrentUser and DB types
5. Any existing feature in backend/app/ — for patterns to follow

Create these files:

1. backend/app/schemas/{{SCHEMA_FILE}}.py
   - {{FeatureName}}Create (request body for POST)
   - {{FeatureName}}Update (request body for PATCH, all fields Optional)
   - {{FeatureName}}Response (response DTO, model_config = ConfigDict(from_attributes=True))
   - Any additional schemas listed in PRD.md (e.g., StreakResponse, MonthlySummaryResponse)
   - Use Pydantic v2 syntax: model_config, Field(), validators with @field_validator

2. backend/app/repositories/{{REPO_FILE}}_repository.py
   - Class: {{FeatureName}}Repository
   - Constructor: __init__(self, db: AsyncSession)
   - All CRUD methods as specified in PRD.md
   - Every DB query MUST filter by user_id
   - Use SQLAlchemy select(), insert(), update(), delete() (not ORM session methods)
   - Methods are async def
   - Return the model instance or None, not raw tuples

3. backend/app/services/{{SERVICE_FILE}}_service.py
   - Class: {{FeatureName}}Service
   - Constructor: __init__(self, repo: {{FeatureName}}Repository)
   - Implements ALL business logic from PRD.md
   - Raises HTTPException for: 404 (not found), 403 (wrong user), 409 (conflict/duplicate), 422 (validation)
   - NO database code in services — only repo calls + logic

4. backend/app/api/v1/{{ROUTER_FILE}}.py
   - FastAPI APIRouter with prefix="/{{url-prefix}}" and tags=["{{Feature Name}}"]
   - All endpoints from PRD.md implemented
   - Every endpoint has: response_model=..., status_code=...
   - Every endpoint uses: user_id: CurrentUser, db: DB (from deps.py)
   - Route handler creates service: service = {{FeatureName}}Service({{FeatureName}}Repository(db))
   - Route handler calls service method and returns result
   - NO logic in route handlers — only service calls

5. Update backend/app/api/v1/router.py:
   - Import the new router
   - Include it: main_router.include_router({{feature}}_router)

Engineering standards (must follow):
- Async def everywhere
- Type hints on all parameters and return types
- No business logic in routes (routes just call services)
- No raw SQL in services (services call repositories)
- All DB queries scoped by user_id

Feature being implemented: {{FEATURE_NAME}}
```

---

## BackendTestAgent

**Purpose:** Write comprehensive pytest tests for one backend feature.

**Prompt Template:**
```
You are writing pytest tests for the {{FEATURE_NAME}} feature of LifeOS.

First read these files:
1. /Users/dev/LifeOS/PRD.md — "{{FEATURE_NAME}}" section. Every listed test case must be covered.
2. /Users/dev/LifeOS/backend/app/api/v1/{{ROUTER_FILE}}.py — the routes to test
3. /Users/dev/LifeOS/backend/app/services/{{SERVICE_FILE}}_service.py — business logic
4. /Users/dev/LifeOS/backend/tests/conftest.py — available fixtures

Create: /Users/dev/LifeOS/backend/tests/test_{{feature}}.py

Test coverage requirements (from PRD.md testing strategy):
1. Happy path — correct input returns correct output + correct HTTP status
2. Auth enforcement — unauthenticated request returns 401
3. Cross-user isolation — user A cannot access/modify user B's data (403)
4. Input validation — invalid input returns 422 with detail message
5. Business logic — all feature-specific rules (streaks, scores, status transitions, etc.)
6. Edge cases — empty results (200 with []), boundary values, duplicate prevention

For each test:
- Use descriptive test names: test_create_small_win_returns_201
- Use the test fixtures from conftest.py
- Mock the database (use the test DB fixture, not a real DB)
- Use pytest.mark.asyncio for async tests
- Assert: status_code, response body fields, DB state changes

After writing all tests, run them:
cd /Users/dev/LifeOS/backend && pytest tests/test_{{feature}}.py -v

Fix any failures before reporting done. All tests must pass.

Target coverage: 85%+ for the new code.
```

---

## FrontendFeatureAgent

**Purpose:** Create React hooks, components, and page for one feature.

**Prompt Template:**
```
You are implementing the frontend for the {{FEATURE_NAME}} feature of LifeOS.

First read these files:
1. /Users/dev/LifeOS/PRD.md — "{{FEATURE_NAME}}" API section (endpoints, request/response shapes)
2. /Users/dev/LifeOS/Context.md — frontend engineering standards
3. /Users/dev/LifeOS/frontend/lib/api.ts — API client to use
4. /Users/dev/LifeOS/frontend/lib/utils.ts — utility functions
5. Any existing feature in frontend/hooks/ or frontend/components/features/ — follow the same patterns
6. /Users/dev/LifeOS/frontend/components/layout/PageWrapper.tsx — use for page layout

Create these files:

1. frontend/hooks/use{{FeatureName}}.ts
   - Use TanStack Query (useQuery, useMutation, useQueryClient)
   - One hook per major operation: use{{FeatureName}}(), useCreate{{FeatureName}}(), useUpdate{{FeatureName}}(), useDelete{{FeatureName}}()
   - Query keys: ['{{feature}}', { date }] etc.
   - useMutation hooks: invalidate relevant queries on success
   - All TypeScript types matching the PRD.md response schemas
   - Export a Types object or interface file alongside

2. frontend/types/{{feature}}.ts
   - TypeScript interfaces matching PRD.md response schemas exactly
   - {{FeatureName}}Response, {{FeatureName}}CreateInput, {{FeatureName}}UpdateInput

3. frontend/components/features/{{feature}}/ (create directory)
   Create components as needed for the feature. At minimum:
   - A form component for creating/editing
   - A list/display component for showing data
   - Any feature-specific analytics components (charts, etc.)

   Component requirements:
   - "use client" only if truly needed (forms and interactive elements need it)
   - Use shadcn/ui primitives (Button, Input, Card, etc.) — no custom HTML elements
   - Handle loading state (skeleton or spinner)
   - Handle error state (error message with retry)
   - Handle empty state (friendly empty message)
   - All props typed with TypeScript interfaces

4. frontend/app/(dashboard)/{{url-path}}/page.tsx
   - Page title as H1
   - Uses PageWrapper component
   - Composes the feature components
   - Date handling: show today by default, allow date switching if feature is date-based

Engineering standards:
- No any types
- All API calls via lib/api.ts
- All server state via React Query hooks
- shadcn/ui for all UI primitives
- Tailwind for styling (no inline styles)

Feature: {{FEATURE_NAME}}
URL path: {{url-path}} (e.g., "small-wins", "workout")
```

---

## FrontendTestAgent

**Purpose:** Write Jest + React Testing Library tests for frontend components.

**Prompt Template:**
```
You are writing Jest + React Testing Library tests for the {{FEATURE_NAME}} frontend.

First read these files:
1. /Users/dev/LifeOS/frontend/components/features/{{feature}}/ — all components to test
2. /Users/dev/LifeOS/frontend/hooks/use{{FeatureName}}.ts — hooks to mock
3. /Users/dev/LifeOS/frontend/app/(dashboard)/{{url-path}}/page.tsx — page to test
4. /Users/dev/LifeOS/PRD.md — "{{FEATURE_NAME}}" frontend test cases

Create test files alongside the components:
- frontend/components/features/{{feature}}/{{Component}}.test.tsx (one per component)
- frontend/app/(dashboard)/{{url-path}}/page.test.tsx

For each component test:
1. Render test — renders without crashing
2. Loading state — shows skeleton/spinner when data is loading
3. Success state — data renders correctly given mock data
4. Error state — error component shown when query fails
5. User interaction — form submits, buttons work, state updates

Testing approach:
- Mock API calls using msw (Mock Service Worker) or jest.mock
- Mock TanStack Query hooks: jest.mock('../hooks/use{{FeatureName}}')
- Use @testing-library/user-event for interactions (not fireEvent)
- Assertions: toBeInTheDocument(), toHaveTextContent(), not.toBeInTheDocument()
- Use screen.getByRole() and screen.getByLabelText() (not getByTestId unless no other option)

After writing all tests, run them:
cd /Users/dev/LifeOS/frontend && npm test -- --testPathPattern={{feature}} --watchAll=false

Fix any failures before reporting done.
```

---

## DashboardBackendAgent

**Purpose:** Create the dashboard aggregation service.

**Prompt Template:**
```
You are implementing the dashboard aggregation backend for LifeOS.

First read these files:
1. /Users/dev/LifeOS/PRD.md — "Feature 9: Dashboard Aggregation" section
2. /Users/dev/LifeOS/Context.md — engineering standards
3. ALL existing repository files in /Users/dev/LifeOS/backend/app/repositories/
4. ALL existing schema files in /Users/dev/LifeOS/backend/app/schemas/

Create these files:

1. backend/app/schemas/dashboard.py
   - DashboardResponse with all fields from PRD.md
   - All fields are Optional (a fresh user has no data — return nulls, not 500s)
   - Nested schemas where needed (e.g., expense_summary_this_month as dict)

2. backend/app/services/dashboard_service.py
   - DashboardService with get_dashboard(user_id, today_date) → DashboardResponse
   - Calls each feature repository
   - Handles missing data gracefully (try/except or None checks)
   - Uses asyncio.gather() for concurrent repository calls (performance)

3. backend/app/api/v1/dashboard.py
   - Single GET /dashboard endpoint
   - Returns DashboardResponse
   - Auth-protected

4. Update router.py to include dashboard router

5. backend/tests/test_dashboard.py
   - Test: no data → all fields null/zero, 200 status (not 500)
   - Test: full data → correct aggregation
   - Test: partial data → nulls where no data, values where data exists
```

---

## DashboardFrontendAgent

**Purpose:** Create all dashboard UI components.

**Prompt Template:**
```
You are implementing the dashboard UI for LifeOS.

First read:
1. /Users/dev/LifeOS/PRD.md — Dashboard Aggregation section (response shape)
2. /Users/dev/LifeOS/frontend/hooks/ — existing hooks for pattern reference
3. /Users/dev/LifeOS/frontend/app/(dashboard)/page.tsx — the page to update

Create:

1. frontend/types/dashboard.ts (DashboardResponse type)

2. frontend/hooks/useDashboard.ts
   - useQuery with key ['dashboard']
   - Calls GET /api/v1/dashboard
   - Refreshes every 5 minutes (staleTime: 5 * 60 * 1000)

3. frontend/components/features/dashboard/IntegrityScoreCard.tsx
   - Shows today's integrity score (0 or 100 or null)
   - Color: green if 100, red if 0, grey if null

4. frontend/components/features/dashboard/WorkoutStreakCard.tsx
   - Shows current streak with flame icon
   - Shows "Did you workout today?" status

5. frontend/components/features/dashboard/ExpenseSummaryCard.tsx
   - Shows monthly total
   - Shows top 3 categories

6. frontend/components/features/dashboard/ResolutionProgressCard.tsx
   - Shows X active resolutions
   - Shows Y completed

7. frontend/components/features/dashboard/Last7DaysChart.tsx
   - Line chart using Recharts
   - Shows integrity score for last 7 days
   - Handles null values gracefully

8. Update frontend/app/(dashboard)/page.tsx
   - "use client"
   - Use useDashboard hook
   - Render all cards in a responsive grid
   - Loading skeleton state
   - Error state
```

---

## EmailReminderAgent

**Purpose:** Implement APScheduler + Resend email reminder system.

**Prompt Template:**
```
You are implementing the email reminder system for LifeOS.

First read:
1. /Users/dev/LifeOS/PRD.md — "Email Reminder System" section
2. /Users/dev/LifeOS/Context.md — env vars (RESEND_API_KEY)
3. /Users/dev/LifeOS/backend/app/main.py — lifespan context manager location
4. /Users/dev/LifeOS/backend/app/repositories/small_win_repository.py — for checking entries

Create:

1. backend/app/services/email_service.py
   - send_small_wins_reminder(user_email: str, user_id: UUID) async
   - Uses resend Python SDK
   - HTML email: friendly reminder to log wins
   - Catches Resend errors, logs them (does not raise — reminder failure must not crash app)

2. backend/app/services/scheduler_service.py
   - create_scheduler() → AsyncIOScheduler
   - Job: daily_reminder_job() — async function
     - Queries all users (for v1: just check if today has no entries for the single user)
     - If no small_wins for today: calls email_service.send_small_wins_reminder()
   - Configures job to run at 20:00 daily (8 PM)
   - Returns configured scheduler (not started — started in lifespan)

3. Update backend/app/main.py lifespan:
   - Create scheduler
   - scheduler.start() at startup
   - scheduler.shutdown() at teardown

4. backend/tests/test_email_reminder.py
   - Test: no entries today + mock Resend → email "would be sent" (assert send called)
   - Test: entries exist today → no email sent (assert send not called)
   - Use pytest-mock to mock resend.Emails.send()

IMPORTANT: The scheduler must use BackgroundScheduler or AsyncIOScheduler properly so it doesn't block the event loop. Use APScheduler 3.x AsyncIOScheduler.
```

---

## FixAgent

**Purpose:** Fix broken code identified by the orchestrator.

**Prompt Template:**
```
You are fixing a bug in the LifeOS codebase.

Context:
- Feature: {{FEATURE_NAME}}
- File to fix: {{FILE_PATH}}
- Error/failure:
  {{ERROR_OUTPUT}}

What the correct behavior should be:
{{EXPECTED_BEHAVIOR}}

Reference: {{PRD_SECTION_OR_STANDARD}} in /Users/dev/LifeOS/PRD.md or /Users/dev/LifeOS/Context.md

Instructions:
1. Read the failing file: {{FILE_PATH}}
2. Read the test that's failing: {{TEST_FILE}}
3. Understand the root cause of the failure
4. Make the minimal change needed to fix it
5. Do NOT refactor other code
6. Do NOT add features
7. Run the failing test again to confirm it passes
8. Report: what was wrong, what you changed, test output

Do not touch any file except {{FILE_PATH}} (and its direct test file if needed).
```

---

## Prompt Construction Guide for Orchestrator

When spawning any sub-agent, use this checklist:

### Required Elements in Every Prompt
1. **Role statement** — "You are [doing X] for LifeOS"
2. **Read-first instructions** — explicit list of files to read before starting
3. **Exact file paths** — every file to create or modify, with full path
4. **Reference to spec** — point to PRD.md section or Context.md standard
5. **Verification step** — how to confirm the work is correct (run tests, start server, etc.)
6. **Constraints** — what NOT to do (no logic in routes, no any types, etc.)

### Variable Substitution Reference
| Variable | Example values |
|---|---|
| `{{FEATURE_NAME}}` | "Small Wins", "Workout Tracking", "Self Assessment" |
| `{{MODEL_FILE}}` | "small_win", "workout", "self_assessment" |
| `{{TABLE_NAME}}` | "small_wins", "workouts", "self_assessments" |
| `{{ModelClass}}` | "SmallWin", "Workout", "SelfAssessment" |
| `{{SCHEMA_FILE}}` | "small_win", "workout", "self_assessment" |
| `{{REPO_FILE}}` | "small_win", "workout", "self_assessment" |
| `{{SERVICE_FILE}}` | "small_win", "workout", "self_assessment" |
| `{{ROUTER_FILE}}` | "small_wins", "workouts", "self_assessment" |
| `{{url-prefix}}` | "/small-wins", "/workouts", "/self-assessment" |
| `{{url-path}}` | "small-wins", "workout", "self-assessment" |
| `{{FeatureName}}` | "SmallWin", "Workout", "SelfAssessment" |
| `{{feature}}` | "small-wins", "workout", "self-assessment" |
