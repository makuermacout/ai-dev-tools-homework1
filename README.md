
# Shared Household Chore Management Tool

A Django web app for managing shared household chores with automated,
accountability-driven rotation between housemates.

## Core Concept

Every recurring chore has a **Doer** (does the task) and an **Inspector**
(peer-reviews it). Roles rotate automatically on a strict calendar schedule,
so accountability doesn't rely on the honor system alone.

## Key Features

- **Peer Approval Verification** — tasks require another housemate to review
  and approve completion before they count as done.
- **Assigned Inspector Roles** — each chore instance has a specific,
  designated inspector, not just any housemate.
- **Automated Fixed Rotation** — the system automatically cycles who's the
  Doer vs. Inspector for each chore.
- **Strict Calendar Scheduling** — rotations advance on fixed dates
  regardless of pending or delayed approvals, with overdue tasks marked
  `MISSED`.

## Tech Stack

- Django 6.1 (Python web framework)
- SQLite (development database)

## Project Structure

- `chore_config/` — Django project settings and root URL configuration
- `chores/` — core app: models, views, forms, admin, rotation engine, tests
- `_docs/plan.md` — original project scope and spec
- `_docs/backlog.md` — development backlog

## Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/Scripts/activate    # Windows (Git Bash)
# source venv/bin/activate      # Mac/Linux

# Install dependencies
pip install django

# Run migrations
python manage.py makemigrations chores
python manage.py migrate

# Create an admin user
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the dashboard, or `http://127.0.0.1:8000/admin/`
for the Django admin panel.

## Running the Rotation Engine

Manually trigger the calendar rollover (normally run on a schedule via cron
or a task scheduler):

```bash
python manage.py rotate_chores
```

## Running Tests

```bash
python manage.py test
```

Test coverage includes model relationships, the rotation engine's
doer/inspector assignment logic, dashboard access control, and the
chore completion/review action views.