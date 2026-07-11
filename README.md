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

## Cloning the repo and navigating through your terminal
From your IDE's terminal use the commands below
```
git clone https://github.com/esantiano/Habit-Tracker-Backend.git
cd Habit-Tracker-Backend
```
Within your IDE open the Habit-Tracker-Backend folder 

## Creating the virtual environment 
This project requires the latest version of python to run locally.

Create a virtual environment
```
python -m venv venv
```
Activate the virtual environment 
mac/linux
```
source venv/bin/activate
```
Activate the virtual environment windows powershell
```
venv\Scripts\Activate.ps1
```
Install required packages on the virtual environment
```
pip install -r requirements.txt
```

## Create .env:
For mac or linux run the following in your terminal
```
touch .env
```
For windows 
```
New-Item .env
```
Copy and paste the following code into the created .env file.
You can generate your own secret key if you prefer.
```
ENV=dev
DATABASE_URL=sqlite:///Habit-Tracker.db
SECRET_KEY=dev-secret
```

## Creating the expected database
Running the terminal command below will create the expected database named in the .env locally.

```
alembic upgrade head
```

## Starting the project

```
uvicorn main:app --reload
```

## Testing

Run backend tests:

```
pytest
```
