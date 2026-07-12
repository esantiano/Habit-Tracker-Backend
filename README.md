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
# Local Development Setup

## Prerequisites
This project requires the latest version of python to run locally.
https://www.python.org/downloads/

## 1. Clone the Repository
```
git clone https://github.com/esantiano/Habit-Tracker-Backend.git
cd Habit-Tracker-Backend
```

## 2. Creating a Virtual Environment 
Create a virtual environment
```
python -m venv venv
```
Activate the virtual environment 
For macOS or Linux
```
source venv/bin/activate
```
For Windows
```
venv\Scripts\Activate.ps1
```

## 3. Install Dependencies
```
pip install -r requirements.txt
```

## 4. Configure Environment Variables:
Create a ```.env``` file in the project root directory
For macOs or Linux
```
touch .env
```
For Windows 
```
New-Item .env
```
Copy and paste the following code into the created .env file.
Replace ```dev-secret``` with your own secret key.
```
ENV=dev
DATABASE_URL=sqlite:///Habit-Tracker.db
SECRET_KEY=dev-secret
```

## 5. Initialize the Database
Apply the Alembic database migrations
```
alembic upgrade head
```

## 6. Starting or Stopping the Development Server
Run the application with Uvicorn:
```
uvicorn main:app --reload
```
Stop the application by pressing: 
Ctrl + C
## Testing

Run backend tests:

```
pytest
```
