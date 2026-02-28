# Habit Tracker API

### FastAPI + PostgreSQL + Alembic

## Overview

This repository contains the backend API for Habit Tracker
The API provides:

- JWT authentication
- Habit CRUD (daily + weekly goals)
- Streak calculation (daily + weekly)
- Analytics endpoints
- GitHub-style heatmap data
- Period-based consistency score
- Soft-delete via archive/restore
- Schema migrations via Alembic

- ## Tech Stack

- FastAPI
- SQLAlchemy ORM
- Alembic (database migrations)
- PostgreSQL (production)
- SQLite (local dev)
- bcrypt (password hashing)
- python-jose (JWT)

- ## Database Design

### Tables

- `users`
- `habits`
- `habit_logs`

### Constraints

- Unique: `(user_id, habit_id, date)`
- Indexed for analytics queries

---

## Key Design Decisions

### Completion Date vs Created Timestamp

`HabitLog.date` represents the day the habit was completed.

`created_at` represents when it was logged.

Prevents streak inconsistencies when logging retroactively.

---

### Period-Based Consistency

Daily habits → evaluated per day

Weekly habits → evaluated per week

Consistency score = successful periods / total periods

---

### Soft Deletes

Habits are archived via `is_archived` instead of hard deletion:

- Preserves historical logs
- Prevents broken foreign keys
- Enables restore functionality

---

## Local Setup

```
git clone <repo-url>
cd backend
python-m venv venv
source venv/bin/activate
pip install-r requirements.txt
```

Create `.env`:

```
ENV=dev
DATABASE_URL=sqlite:///./dev.db
SECRET_KEY=dev-secret
```

Run migrations:

```
alembic upgrade head
```

Start server:

```
uvicorn main:app--reload
```

## Testing

Run backend tests:

```
pytest
```
