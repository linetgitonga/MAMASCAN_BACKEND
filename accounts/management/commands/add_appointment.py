from django.core.management.base import BaseCommand
from django.utils import timezone
from appointments.models import Appointment, Client, Staff, Service
import random
import datetime

class Command(BaseCommand):
    help = "Populate the database with dummy appointments"

    def handle(self, *args, **kwargs):
        clients = list(Client.objects.all())
        staff_members = list(Staff.objects.all())
        services = list(Service.objects.filter(is_active=True))

        if not clients or not staff_members or not services:
            self.stdout.write(self.style.ERROR("You need clients, staff, and services in the database first!"))
            return

        status_choices = [choice[0] for choice in Appointment.STATUS_CHOICES]
        today = timezone.now().date()

        for i in range(100):
            client = random.choice(clients)
            staff = random.choice(staff_members)
            service = random.choice(services)
            # Appointments within +/- 40 days from today
            appointment_date = today + datetime.timedelta(days=random.randint(-40, 20))
            # Random time between 8am and 5pm
            appointment_time = datetime.time(hour=random.randint(8, 17), minute=random.choice([0, 15, 30, 45]))
            status = random.choice(status_choices)
            notes = f"{client.first_name} {client.last_name} booked {service.name} with {staff.first_name} on {appointment_date.strftime('%Y-%m-%d')} at {appointment_time.strftime('%H:%M')}"
            internal_notes = "N/A"
            reminder_sent = random.choice([True, False])

            # Avoid duplicate (staff, date, time)
            if Appointment.objects.filter(staff=staff, appointment_date=appointment_date, appointment_time=appointment_time).exists():
                continue

            Appointment.objects.create(
                client=client,
                staff=staff,
                service=service,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status=status,
                notes=notes,
                internal_notes=internal_notes,
                reminder_sent=reminder_sent,
            )

        self.stdout.write(self.style.SUCCESS("Dummy appointments created successfully!"))