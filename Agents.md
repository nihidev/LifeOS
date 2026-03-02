# LifeOS — Agent Orchestration Guide

**For:** Claude Code (Orchestrator Agent)
**Version:** 1.0

This document defines how Claude Code should orchestrate work on the LifeOS project — which agents to spawn, when to spawn them in parallel vs. sequentially, how to validate their output, and what the overall build loop looks like.

---

## Orchestrator Role

The **orchestrator** (the top-level Claude Code instance) is responsible for:

1. Reading and understanding `Context.md`, `PRD.md`, `Featureslist.md` before any work
2. Breaking each phase into discrete, parallelizable sub-tasks
3. Spawning sub-agents from `SubAgents.md` with precise, self-contained prompts
4. Validating sub-agent output before merging
5. Updating `Featureslist.md` as tasks complete
6. Never writing code directly — always delegating to typed sub-agents
7. Catching sub-agent errors and retrying with correction context

---

## Guiding Principles for Orchestration

### 1. Read First, Always
Before starting any phase, the orchestrator must:
```
1. Read Context.md       → understand stack, structure, standards
2. Read PRD.md           → understand the exact feature spec
3. Read Featureslist.md  → understand what's done, what's next
4. Read existing code    → understand what's already been built
```
Never spawn a sub-agent without reading the relevant existing code first.

### 2. Phase-Gate Enforcement
Each phase has hard dependencies. Do not start Phase N+1 until Phase N is verified complete.

```
Phase 0 (Bootstrap) → must pass: server starts, /health OK, auth middleware working
Phase 1 (Small Wins) → must pass: all backend tests green, frontend renders
Phase 2 (Workout) → must pass: streak calculation tested and correct
... etc.
```

Verification method: Run tests, read output, confirm zero failures before proceeding.

### 3. Parallel Where Safe, Sequential Where Not

**Safe to parallelize:**
- Backend + Frontend work for the same feature (they have no code dependency)
- Multiple independent feature implementations (once Phase 0 is done)
- Tests for different features
- Linting + testing

**Must be sequential:**
- Alembic migration generation → migration application → service/repo code (must know the actual schema)
- Frontend API hook → Frontend component (hook must exist first)
- Phase N+1 after Phase N (hard dependency)

### 4. Sub-Agent Prompt Quality
A bad sub-agent prompt produces bad code. Every sub-agent prompt must include:
- Exact file paths to create or modify
- The specific task (not "implement the feature" — be explicit)
- Reference to which PRD.md section to follow
- The engineering standards from Context.md
- Any existing code that the new code must be compatible with

---

## Phase-by-Phase Orchestration Plan

### Phase 0 — Bootstrap

**All sequential.** No parallelism possible — each step is a foundation for the next.

```
Step 1: Spawn [ScaffoldAgent]
  → Create monorepo directory structure
  → Create .gitignore
  → Initialize git

Step 2: Spawn [BackendBootstrapAgent]
  → Create requirements.txt
  → Create core/ (config, database, security, deps)
  → Create main.py
  → Create api/v1/router.py (empty)
  → Verify: uvicorn starts

Step 3: Spawn [AlembicSetupAgent]
  → alembic init
  → Configure env.py for async

Step 4: Spawn [FrontendBootstrapAgent]
  → create-next-app
  → Install all dependencies
  → Create lib/ files
  → Create layout and login page
  → Verify: npm run dev works

Step 5: Spawn [CISetupAgent]
  → Create .github/workflows/backend.yml
  → Create .github/workflows/frontend.yml
```

**Phase 0 Exit Criteria:**
- [ ] `GET /health` returns 200
- [ ] JWT middleware rejects unauthorized request with 401
- [ ] `GET /login` renders in browser
- [ ] `pytest` runs (0 tests = OK, no errors)
- [ ] `npm run build` passes

---

### Phase 1 — Small Wins

**Parallel execution possible:** Backend and Frontend can run simultaneously.

```
[SEQUENTIAL FIRST]
Step 1: Spawn [ModelMigrationAgent]
  → Create app/models/small_win.py
  → Generate Alembic migration
  → Apply migration

[THEN PARALLEL]
Step 2a: Spawn [BackendFeatureAgent("small_wins")]
  → Create schemas/small_win.py
  → Create repositories/small_win_repository.py
  → Create services/small_win_service.py
  → Create api/v1/small_wins.py
  → Register in router.py

Step 2b: Spawn [FrontendFeatureAgent("small-wins")]
  → Create hooks/useSmallWins.ts
  → Create components/features/small-wins/
  → Create app/(dashboard)/small-wins/page.tsx

[THEN PARALLEL]
Step 3a: Spawn [BackendTestAgent("small_wins")]
  → Write tests/test_small_wins.py
  → Run pytest, confirm all pass

Step 3b: Spawn [FrontendTestAgent("small-wins")]
  → Write tests/ for small wins components
  → Run jest, confirm all pass

[THEN]
Step 4: Spawn [EmailReminderAgent]
  → Create services/email_service.py
  → Create services/scheduler_service.py
  → Wire into main.py lifespan
```

**Phase 1 Exit Criteria:**
- [ ] All 8 backend test cases pass
- [ ] Frontend page renders with working CRUD
- [ ] Email reminder service starts without error

---

### Phase 2 — Workout Tracking

```
[SEQUENTIAL FIRST]
Step 1: Spawn [ModelMigrationAgent("workouts")]

[PARALLEL]
Step 2a: Spawn [BackendFeatureAgent("workouts")]
Step 2b: Spawn [FrontendFeatureAgent("workout")]

[PARALLEL]
Step 3a: Spawn [BackendTestAgent("workouts")]  ← CRITICAL: test streak logic
Step 3b: Spawn [FrontendTestAgent("workout")]
```

---

### Phases 3, 4, 5 — Self Assessment, Expenses, Resolutions

Same pattern as Phase 2. Each can be orchestrated the same way.

**Note on Phase 5 (Resolutions):** The status transition business logic is in the service layer. Ensure [BackendTestAgent] explicitly tests all status transitions.

---

### Phase 6 — Dashboard Aggregation

**Must run after Phases 1–5 are complete.** Dashboard calls all feature repositories.

```
Step 1: Spawn [DashboardBackendAgent]
  → Read all existing repositories
  → Create services/dashboard_service.py
  → Create schemas/dashboard.py
  → Create api/v1/dashboard.py

Step 2: Spawn [DashboardTestAgent]
  → Test null/empty state
  → Test full data state
  → Test partial data state

[PARALLEL]
Step 3a: Spawn [DashboardFrontendAgent]
  → Create dashboard cards components
  → Update app/(dashboard)/page.tsx
Step 3b: Already done above
```

---

### Phase 7 — Email Hardening

```
Step 1: Spawn [EmailHardeningAgent]
  → Add error handling
  → Add idempotency check
  → Write integration tests with mock Resend
```

---

### Phases 8–9 — Secondary Features + CI/CD

Secondary features (Food Logs, Grocery, Appointments) follow the same pattern as Phases 2–5.

Phase 9 is infrastructure-only:
```
Step 1: Spawn [CIHardeningAgent]
  → Finalize GitHub Actions workflows
  → Add docker-compose.yml
  → Add Makefile
  → Ensure coverage ≥ 85%
```

---

## Validation After Each Sub-Agent

After every sub-agent completes, the orchestrator must:

1. **Read the created/modified files** — verify they match the spec
2. **Run the relevant tests** — no assumed success
3. **Check for common errors:**
   - Missing auth check on route (`Depends(get_current_user)` present?)
   - Business logic inside route handler (should be in service)
   - Raw SQL instead of repository pattern
   - Missing user_id scope in DB queries
   - `any` types in TypeScript
   - Hardcoded strings instead of env config
4. **If errors found:** Spawn a [FixAgent] with specific error context and the file to fix

---

## Error Recovery Protocol

When a sub-agent produces incorrect output:

```
1. Identify the specific error(s)
2. Read the failing test output or error message
3. Spawn [FixAgent] with:
   - The exact error message
   - The file that needs fixing
   - What the correct behavior should be (reference PRD.md section)
   - The current broken code
4. Re-run tests to confirm fix
5. If still failing after 2 attempts: stop and report to user
```

---

## Git Workflow for Agents

### Branch Strategy
```
main          → production-ready, protected
develop       → integration branch
feature/*     → feature branches (one per phase/feature)
```

### Commit Convention
```
feat: add small wins CRUD endpoints
feat: add workout streak calculation
fix: correct expense category aggregation
test: add self assessment unit tests
chore: add GitHub Actions CI workflow
```

Sub-agents should commit to `feature/<feature-name>` branches.
The orchestrator merges feature branches into `develop` after validation.
`develop` → `main` is a manual step (user does this).

### Agent Git Commits
Each sub-agent that completes a unit of work should:
```bash
git add <specific files only>   # Never git add -A
git commit -m "feat: <description>"
```

---

## Communication Standards

When reporting to the user, the orchestrator should:

1. State what phase is being executed
2. List which sub-agents are being spawned (and whether in parallel)
3. Report sub-agent completion with: files created, tests passed/failed
4. Flag any deviation from the spec
5. Ask for input only when genuinely blocked (not for confirmation of obvious steps)

---

## Anti-Patterns (Never Do These)

| Anti-Pattern | Correct Approach |
|---|---|
| Write all features at once | Follow the phase gate system |
| Start feature work without reading existing code | Always read relevant files first |
| Let sub-agent run without a precise prompt | Write specific, file-path-level prompts |
| Skip test validation | Run tests after every sub-agent |
| Merge to main without passing CI | Only merge when all tests green |
| Put business logic in route handlers | Routes call services only |
| Skip the repo pattern | All DB access through repositories |
| Use `any` in TypeScript | Strict typing always |
| Hardcode secrets | Everything via env config |
