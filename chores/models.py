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
    # Fixed typo from related_related_name to related_name
    doer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_tasks")
    inspector = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_inspections")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    start_date = models.DateField()
    due_date = models.DateField()
    
    completed_at = models.DateTimeField(null=True, blank=True)
    inspected_at = models.DateTimeField(null=True, blank=True)
    rejection_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.chore_definition.title} - Doer: {self.doer.username} | Inspector: {self.inspector.username}"