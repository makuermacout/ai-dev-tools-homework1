# Shared Household Chore Management Tool - Project Scope

## Executive Summary
This document outlines the product scope, core workflow, system architecture, and database design for a Django-based web application designed to enforce household chore accountability through automated fixed rotations and designated peer inspections.

---

## 1. Core Objectives & System Scope

| Feature / Layer | Specification Details |
| :--- | :--- |
| **Primary Focus** | **Accountability:** Track task completion transparently across housemates. |
| **Verification Method** | **Peer Approval:** Tasks must be reviewed and approved by another housemate. |
| **Reviewer Structure** | **Assigned Inspector:** Each recurring task has a designated inspector. |
| **Assignment Model** | **Fixed Rotation:** The system automatically cycles doers and inspectors across recurring intervals. |
| **Schedule Engine** | **Strict Calendar:** Rotations advance on fixed calendar dates regardless of pending approvals. |
| **Technology Stack** | **Django (Python Web Framework)** with SQLite/PostgreSQL, Celery/Django-Q for scheduled tasks, and responsive CSS/HTML templates. |

---

## 2. Core Operational Workflows

### 2.1 The Chore Lifecycle
1. **Schedule Generation:** On the scheduled rotation date (e.g., every Monday at 00:00), the system generates a active `ChoreInstance` assigning a **Doer** and an **Inspector** based on predefined household rotation rules.
2. **Task Execution:** The assigned **Doer** completes the physical chore and clicks "Mark as Complete" in the web dashboard.
3. **Inspection Trigger:** The status shifts to `Pending Inspection`, notifying the assigned **Inspector**.
4. **Peer Review:**
   - **Approved:** The task status changes to `Completed`.
   - **Rejected:** The **Inspector** provides feedback/rejection notes. The status returns to `In Progress` for the **Doer** to rectify.
5. **Calendar Rollover:** At the end of the strict calendar window, if a chore remains uncompleted or unapproved, it is marked `Overdue`/`Missed`, and the next calendar cycle triggers the next rotation.

---

## 3. Recommended Data Model (Django Schema)

Below is the conceptual structure for the Django models supporting this application:

```python
from django.db import models
from django.contrib.auth.models import User

class Household(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class HouseholdMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="members")
    rotation_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} ({self.household.name})"

class ChoreDefinition(models.Model):
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('BIWEEKLY', 'Bi-Weekly'),
        ('MONTHLY', 'Monthly'),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="chores")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='WEEKLY')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class ChoreInstance(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Execution'),
        ('NEEDS_INSPECTION', 'Needs Inspection'),
        ('APPROVED', 'Approved & Completed'),
        ('REJECTED', 'Rejected / Needs Rework'),
        ('MISSED', 'Missed / Overdue'),
    ]

    chore_definition = models.ForeignKey(ChoreDefinition, on_delete=models.CASCADE, related_name="instances")
    doer = models.ForeignKey(User, on_delete=models.CASCADE, related_related_name="assigned_tasks")
    inspector = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_inspections")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    start_date = models.DateField()
    due_date = models.DateField()
    
    completed_at = models.DateTimeField(null=True, blank=True)
    inspected_at = models.DateTimeField(null=True, blank=True)
    rejection_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.chore_definition.title} - Doer: {self.doer.username} | Inspector: {self.inspector.username}"
```

---

## 4. Key Milestones & Roadmap

1. **Phase 1: Project Setup & Authentication**
   - Django project initialization
   - User registration, household creation, and member invitation workflows
2. **Phase 2: Chore Management & Rotation Engine**
   - Setup `ChoreDefinition` interface
   - Automated logic to calculate next doer/inspector based on `rotation_order`
   - Background job runner (e.g., Celery or Django Management Commands run via Cron) for strict calendar rollovers
3. **Phase 3: Inspection Dashboard & Interface**
   - Mobile-responsive web view for pending tasks
   - Peer review UI: One-tap Approve/Reject buttons with optional notes
4. **Phase 4: Notifications & History Log**
   - Email/Webpush alerts for inspection requests and rejections
   - Transparency log to view historical chore adherence
