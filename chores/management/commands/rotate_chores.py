from datetime import date, timedelta
from django.core.management.base import BaseCommand
from chores.models import ChoreDefinition, ChoreInstance
from chores.services import get_next_doer_and_inspector


class Command(BaseCommand):
    help = "Rotates completed or expired chores and generates the next cycle instances based on strict calendar limits."

    def handle(self, *args, **options):
        today = date.today()
        active_definitions = ChoreDefinition.objects.filter(is_active=True)
        created_count = 0

        for chore_def in active_definitions:
            latest_instance = (
                ChoreInstance.objects.filter(chore_definition=chore_def)
                .order_by('-due_date')
                .first()
            )

            # Check if active cycle exists and is still within calendar window
            if latest_instance and latest_instance.due_date >= today:
                continue

            # Mark overdue pending tasks as MISSED (Strict Calendar Rule)
            if latest_instance and latest_instance.status in ['PENDING', 'NEEDS_INSPECTION', 'REJECTED']:
                latest_instance.status = 'MISSED'
                latest_instance.save()

            # Determine doer & inspector for the next rotation
            current_doer = latest_instance.doer if latest_instance else None
            next_doer, next_inspector = get_next_doer_and_inspector(chore_def, current_doer)

            # Set duration based on frequency
            duration_days = 7
            if chore_def.frequency == 'DAILY':
                duration_days = 1
            elif chore_def.frequency == 'BIWEEKLY':
                duration_days = 14
            elif chore_def.frequency == 'MONTHLY':
                duration_days = 30

            due_date = today + timedelta(days=duration_days)

            # Create new ChoreInstance
            ChoreInstance.objects.create(
                chore_definition=chore_def,
                doer=next_doer,
                inspector=next_inspector,
                status='PENDING',
                start_date=today,
                due_date=due_date
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully rotated chores! Generated {created_count} new task instance(s).")
        )