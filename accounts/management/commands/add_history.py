from django.core.management.base import BaseCommand
from django.utils import timezone
from appointments.models import Appointment, AppointmentHistory
from accounts.models import User
import random

STATUS_FLOW = [
    ('scheduled', 'confirmed'),
    ('confirmed', 'in_progress'),
    ('in_progress', 'completed'),
    ('scheduled', 'cancelled'),
    ('confirmed', 'cancelled'),
    ('scheduled', 'no_show'),
]

class Command(BaseCommand):
    help = "Populate the database with dummy appointment history records"

    def handle(self, *args, **kwargs):
        users = list(User.objects.all())
        appointments = list(Appointment.objects.all())
        if not users or not appointments:
            self.stdout.write(self.style.ERROR("You need users and appointments in the database first!"))
            return

        count = 0
        for appointment in appointments:
            # Simulate 1-3 status changes per appointment
            num_changes = random.randint(1, 3)
            current_status = appointment.status
            for _ in range(num_changes):
                # Pick a possible status transition
                possible_flows = [flow for flow in STATUS_FLOW if flow[0] == current_status]
                if not possible_flows:
                    break
                flow = random.choice(possible_flows)
                previous_status, new_status = flow
                changed_by = random.choice(users)
                notes = f"Status changed from {previous_status} to {new_status} by {changed_by.get_full_name()}"
                AppointmentHistory.objects.create(
                    appointment=appointment,
                    previous_status=previous_status,
                    new_status=new_status,
                    changed_by=changed_by,
                    changed_at=timezone.now(),
                    notes=notes,
                )
                current_status = new_status
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Dummy appointment history records created: {count}"))