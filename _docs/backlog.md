# Django Shared Household Chore Management - Development Backlog

## Phase 1: Foundation & Authentication
- [ ] **Task 1.1: Core App & User Management Setup**
  - Implement `Household` and `HouseholdMember` models.
  - Create registration, login, and household creation/joining views.
- [ ] **Task 1.2: Fix Schema Typo**
  - Fix the `related_related_name="assigned_tasks"` typo in `ChoreInstance.doer` to `related_name="assigned_tasks"`.

## Phase 2: Core Data Models & Admin Interface
- [ ] **Task 2.1: Define Chore Models**
  - Create `ChoreDefinition` and `ChoreInstance` models with status choices and foreign keys.
  - Run initial migrations (`python manage.py makemigrations && python manage.py migrate`).
- [ ] **Task 2.2: Configure Django Admin**
  - Register `Household`, `HouseholdMember`, `ChoreDefinition`, and `ChoreInstance` in `admin.py` for easy testing and debugging.

## Phase 3: Rotation Engine & Business Logic
- [ ] **Task 3.1: Implement Rotation Engine**
  - Write helper utility functions to calculate the next **Doer** and **Inspector** using `HouseholdMember.rotation_order`.
- [ ] **Task 3.2: Automated Calendar Rollover**
  - Create a custom Django management command (`python manage.py rotate_chores`) to check calendar windows, mark incomplete tasks as `MISSED`, and spawn new `ChoreInstance` records.

## Phase 4: Frontend Views & Workflow Integration
- [ ] **Task 4.1: Dashboard View**
  - Implement a central responsive view showing active chores assigned to the current user as a **Doer** and tasks waiting for them as an **Inspector**.
- [ ] **Task 4.2: Execution & Inspection Action Handlers**
  - Implement view handlers for **Doer** action (`Mark as Complete` -> set status to `NEEDS_INSPECTION`).
  - Implement view handlers for **Inspector** actions (`Approve` / `Reject` with feedback notes).