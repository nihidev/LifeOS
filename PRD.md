# LifeOS — Product Requirements Document (v1)

**Version:** 1.0
**Date:** 2026-03-02
**Status:** Active
**Target User (v1):** Single user (developer)

---

## 1. Executive Summary

LifeOS is a personal discipline and accountability dashboard. It provides structured daily tracking of:

- **Discipline** — workout streaks, small wins momentum
- **Integrity** — relationship quality self-assessment
- **Financial awareness** — expense tracking and categorization
- **Physical consistency** — workout logging
- **Long-term resolution tracking** — goal progress over time

The app prioritizes **minimal daily friction** (quick data entry) with **deep analytical insight** (streaks, trends, aggregate scores).

---

## 2. System Architecture

### High-Level

```
User Browser
    ↓ HTTPS
Next.js Frontend (port 3000)
    ↓ REST API calls (Bearer JWT)
FastAPI Backend (port 8000)
    ├── Supabase Auth (JWT validation)
    ├── Supabase Postgres (via asyncpg)
    └── Resend API (email)
```

### Data Flow Rules
- Frontend never queries the DB directly (no Supabase client DB calls in v1 — all via FastAPI)
- Supabase is used only for Auth in the frontend (magic link flow)
- All business logic lives in the backend service layer
- The frontend is a thin client: fetch data, render it, handle user input

---

## 3. Database Schema

### Conventions
- All PKs: `UUID DEFAULT gen_random_uuid()`
- All tables have `user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE`
- All tables have `created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
- `date DATE` columns represent the "logical date" of the entry (user's local date)
- Supabase RLS enabled on all tables (backup to app-layer user_id scoping)

### small_wins
```sql
CREATE TABLE small_wins (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date        DATE NOT NULL,
    text        TEXT NOT NULL CHECK (char_length(text) > 0),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_small_wins_user_date ON small_wins(user_id, date);
```

### workouts
```sql
CREATE TABLE workouts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    did_workout     BOOLEAN NOT NULL,
    activity_type   TEXT,
    duration_mins   INTEGER,
    notes           TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);
CREATE INDEX idx_workouts_user_date ON workouts(user_id, date DESC);
```

### self_assessments
```sql
CREATE TABLE self_assessments (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date                    DATE NOT NULL,
    performed_well_partner  BOOLEAN NOT NULL,
    note                    TEXT,
    integrity_score         INTEGER NOT NULL CHECK (integrity_score BETWEEN 0 AND 100),
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);
CREATE INDEX idx_self_assessments_user_date ON self_assessments(user_id, date DESC);
```

### expenses
```sql
CREATE TABLE expenses (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date        DATE NOT NULL,
    amount      NUMERIC(10, 2) NOT NULL CHECK (amount > 0),
    category    TEXT NOT NULL CHECK (char_length(category) > 0),
    note        TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_expenses_user_date ON expenses(user_id, date DESC);
CREATE INDEX idx_expenses_user_category ON expenses(user_id, category);
```

### resolutions
```sql
CREATE TABLE resolutions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title             TEXT NOT NULL CHECK (char_length(title) > 0),
    description       TEXT,
    status            TEXT NOT NULL DEFAULT 'not_started'
                          CHECK (status IN ('not_started', 'in_progress', 'completed')),
    progress_percent  INTEGER NOT NULL DEFAULT 0
                          CHECK (progress_percent BETWEEN 0 AND 100),
    target_date       DATE,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### food_logs
```sql
CREATE TABLE food_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date        DATE NOT NULL,
    meal_type   TEXT NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    description TEXT NOT NULL,
    calories    INTEGER,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_food_logs_user_date ON food_logs(user_id, date DESC);
```

### grocery_items
```sql
CREATE TABLE grocery_items (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    item        TEXT NOT NULL CHECK (char_length(item) > 0),
    quantity    TEXT,
    checked     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### appointments
```sql
CREATE TABLE appointments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    start_time  TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time    TIMESTAMP WITH TIME ZONE,
    description TEXT,
    location    TEXT,
    source      TEXT NOT NULL DEFAULT 'manual'
                    CHECK (source IN ('manual', 'google', 'apple')),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_appointments_user_time ON appointments(user_id, start_time ASC);
```

---

## 4. API Specification

### Auth Model
All endpoints (except `/health`) require:
```
Authorization: Bearer <supabase_jwt>
```
Backend validates JWT signature using Supabase JWT secret. Returns 401 if invalid/missing.

---

### Feature 1: Small Wins

**Purpose:** Build psychological momentum through logging daily micro-wins.

**Business Rules:**
- Unlimited entries per day
- Text must be non-empty, max 500 chars
- Users can edit or delete their own entries only
- Entries are soft-date: linked to `date` field, not `created_at`

**Endpoints:**

```
POST   /api/v1/small-wins
Body:  { date: string (YYYY-MM-DD), text: string }
Resp:  SmallWinResponse

GET    /api/v1/small-wins
Query: date=YYYY-MM-DD (required)
Resp:  SmallWinResponse[]

PATCH  /api/v1/small-wins/{id}
Body:  { text: string }
Resp:  SmallWinResponse

DELETE /api/v1/small-wins/{id}
Resp:  { message: "deleted" }
```

**Response Schema:**
```json
{
  "id": "uuid",
  "date": "2026-01-15",
  "text": "Finished the API design",
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-01-15T10:00:00Z"
}
```

---

### Feature 2: Workout Tracking

**Purpose:** Log daily workouts and calculate consistency streaks.

**Business Rules:**
- One entry per user per day (UPSERT behavior — POST to same date replaces)
- `did_workout = false` is a valid entry (rest day logging)
- Streak = consecutive days where `did_workout = true` up to today
- Monthly summary = count of workout days in given month

**Endpoints:**

```
POST   /api/v1/workouts
Body:  { date: string, did_workout: boolean, activity_type?: string,
         duration_mins?: integer, notes?: string }
Resp:  WorkoutResponse

GET    /api/v1/workouts
Query: date=YYYY-MM-DD
Resp:  WorkoutResponse | null

GET    /api/v1/workouts/streak
Resp:  { current_streak: int, longest_streak: int }

GET    /api/v1/workouts/monthly-summary
Query: year=int, month=int
Resp:  { month: string, total_days: int, workout_days: int, rest_days: int,
         completion_percent: float, entries: WorkoutResponse[] }
```

**Streak Algorithm:**
```
Start from today, walk backwards day by day.
Count consecutive days where did_workout = true.
Stop at first gap or missing entry.
```

---

### Feature 3: Self Assessment

**Purpose:** Daily integrity check on relationship quality.

**Business Rules:**
- One entry per user per day
- `integrity_score`: `performed_well_partner = true` → 100, `false` → 0
- Score formula is intentionally binary in v1 (expandable later)
- POST to existing date overwrites (UPSERT)

**Endpoints:**

```
POST   /api/v1/self-assessment
Body:  { date: string, performed_well_partner: boolean, note?: string }
Resp:  SelfAssessmentResponse

GET    /api/v1/self-assessment
Query: date=YYYY-MM-DD
Resp:  SelfAssessmentResponse | null

GET    /api/v1/self-assessment/history
Query: limit=int (default 30), offset=int (default 0)
Resp:  { entries: SelfAssessmentResponse[], average_score: float }
```

**Response Schema:**
```json
{
  "id": "uuid",
  "date": "2026-01-15",
  "performed_well_partner": true,
  "note": "Had a great conversation",
  "integrity_score": 100,
  "created_at": "...",
  "updated_at": "..."
}
```

---

### Feature 4: Expenses

**Purpose:** Track daily spending with category breakdown.

**Business Rules:**
- Multiple entries per day (unlike workouts)
- `amount` must be positive (> 0)
- `category` is free text in v1 (no predefined list)
- Monthly summary groups by category

**Endpoints:**

```
POST   /api/v1/expenses
Body:  { date: string, amount: float, category: string, note?: string }
Resp:  ExpenseResponse

GET    /api/v1/expenses
Query: month=YYYY-MM (required)
Resp:  ExpenseResponse[]

GET    /api/v1/expenses/summary
Query: month=YYYY-MM
Resp:  { month: string, total: float,
         by_category: [{ category: string, total: float, count: int }] }

DELETE /api/v1/expenses/{id}
Resp:  { message: "deleted" }
```

---

### Feature 5: Resolutions

**Purpose:** Track long-term goals with status and progress.

**Business Rules:**
- Status transitions: `not_started` → `in_progress` → `completed`
- `progress_percent` must be 0–100
- When `status = completed`, `progress_percent` auto-set to 100
- No delete in v1 (preserve history)

**Endpoints:**

```
POST   /api/v1/resolutions
Body:  { title: string, description?: string, target_date?: string }
Resp:  ResolutionResponse

GET    /api/v1/resolutions
Query: status? (filter by status)
Resp:  ResolutionResponse[]

PATCH  /api/v1/resolutions/{id}
Body:  { title?: string, description?: string, status?: string,
         progress_percent?: int, target_date?: string }
Resp:  ResolutionResponse
```

---

### Feature 6: Food Logs

**Purpose:** Simple meal tracking without calorie obsession.

**Endpoints:**

```
POST   /api/v1/food-logs
Body:  { date: string, meal_type: string, description: string, calories?: int }
Resp:  FoodLogResponse

GET    /api/v1/food-logs
Query: date=YYYY-MM-DD
Resp:  FoodLogResponse[]

DELETE /api/v1/food-logs/{id}
Resp:  { message: "deleted" }
```

---

### Feature 7: Grocery List

**Purpose:** Persistent checklist, not date-based.

**Endpoints:**

```
POST   /api/v1/grocery
Body:  { item: string, quantity?: string }
Resp:  GroceryItemResponse

GET    /api/v1/grocery
Resp:  GroceryItemResponse[]

PATCH  /api/v1/grocery/{id}
Body:  { item?: string, quantity?: string, checked?: boolean }
Resp:  GroceryItemResponse

DELETE /api/v1/grocery/{id}
Resp:  { message: "deleted" }

POST   /api/v1/grocery/clear-checked
Resp:  { deleted_count: int }
```

---

### Feature 8: Appointments

**Purpose:** Simple calendar for upcoming events (manual entry in v1).

**Endpoints:**

```
POST   /api/v1/appointments
Body:  { title: string, start_time: datetime, end_time?: datetime,
         description?: string, location?: string }
Resp:  AppointmentResponse

GET    /api/v1/appointments
Query: from=YYYY-MM-DD, to=YYYY-MM-DD
Resp:  AppointmentResponse[]

PATCH  /api/v1/appointments/{id}
Body:  (any appointment field)
Resp:  AppointmentResponse

DELETE /api/v1/appointments/{id}
Resp:  { message: "deleted" }
```

---

### Feature 9: Dashboard Aggregation

**Purpose:** Single endpoint for all today's summary data.

```
GET    /api/v1/dashboard
Resp:
{
  "date": "2026-01-15",
  "integrity_score_today": 100,
  "workout_streak": 7,
  "did_workout_today": true,
  "monthly_expense_total": 1243.50,
  "active_resolutions": 3,
  "completed_resolutions": 1,
  "small_wins_today": 2,
  "last_7_days_integrity": [100, 0, 100, 100, 100, 0, 100],
  "expense_summary_this_month": {
    "Food": 450.00,
    "Transport": 120.00,
    "Entertainment": 80.00
  }
}
```

---

## 5. Email Reminder System

**Trigger:** Daily cron at user-configured time (default: 8:00 PM local time)

**Logic:**
```
For each user:
  if no small_wins entry for today:
    send reminder email via Resend
```

**Email content:** Simple HTML — "You haven't logged your wins today. Don't break the streak!"

**Implementation:**
- `APScheduler` `AsyncIOScheduler` runs inside FastAPI lifespan
- Uses `BackgroundTasks` or direct async call to Resend
- Job is idempotent — safe to re-run

---

## 6. Non-Functional Requirements

| Requirement | Target |
|---|---|
| API response time (p95) | < 200ms |
| Frontend initial load | < 2s on 4G |
| Test coverage (BE) | ≥ 85% |
| Auth token validation | < 10ms |
| Concurrent users (v1) | 1 (single user app) |
| Uptime target | Best effort (personal app) |
| Data retention | Indefinite |

---

## 7. Error Handling Standards

### Backend Error Responses
All errors return:
```json
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE_SNAKE_CASE"
}
```

| Scenario | HTTP Status |
|---|---|
| Missing/invalid JWT | 401 |
| Resource belongs to other user | 403 |
| Resource not found | 404 |
| Validation error (Pydantic) | 422 |
| Duplicate entry (UNIQUE violation) | 409 |
| Server error | 500 |

### Frontend Error Handling
- React Query `onError` callbacks show toast notifications
- Form validation errors shown inline
- Network errors show retry prompt
- Auth errors redirect to `/login`

---

## 8. Testing Strategy

### Backend Tests (pytest)
Each feature has its own test file. Every test file covers:

1. **Happy path** — correct input returns correct output
2. **Auth enforcement** — unauthenticated request returns 401
3. **Cross-user isolation** — user A cannot access user B's data
4. **Validation** — invalid input returns 422 with clear message
5. **Business logic** — feature-specific rules (streak calc, score calc, etc.)
6. **Edge cases** — empty results, boundary values, duplicates

### Frontend Tests (Jest + RTL)
Each page/component has:

1. **Render test** — component renders without crashing
2. **Loading state** — shows skeleton/spinner during fetch
3. **Success state** — data displays correctly
4. **Error state** — error message shown
5. **User interaction** — form submit, button click, optimistic update

---

## 9. Future Scope (v2+)

- Google Calendar OAuth integration for appointments
- Apple Calendar ICS sync
- Multi-user support with teams/accountability partners
- Mobile app (React Native or PWA)
- Weekly email digest (not just daily reminder)
- Integrity score expansion (multiple self-assessment questions)
- Export to CSV/PDF
- Dark mode
