from django.core.management.base import BaseCommand
from appointments.models import Service

SERVICES = [
    {
        "name": "Initial Consultation",
        "description": "First-time patient consultation with a clinician.",
        "duration": 30,
        "price": 1000.00,
    },
    {
        "name": "Follow-up Visit",
        "description": "Follow-up appointment to review patient progress.",
        "duration": 20,
        "price": 800.00,
    },
    {
        "name": "Pap Smear",
        "description": "Screening procedure for cervical cancer.",
        "duration": 20,
        "price": 1500.00,
    },
    {
        "name": "Pelvic Ultrasound",
        "description": "Imaging of pelvic organs.",
        "duration": 40,
        "price": 3500.00,
    },
    {
        "name": "CA-125 Blood Test",
        "description": "Blood test for ovarian cancer marker.",
        "duration": 15,
        "price": 2000.00,
    },
    {
        "name": "Ovarian Cystectomy",
        "description": "Surgical removal of ovarian cyst.",
        "duration": 120,
        "price": 20000.00,
    },
    {
        "name": "Pain Management",
        "description": "Consultation and prescription for pain relief.",
        "duration": 15,
        "price": 700.00,
    },
    {
        "name": "Urinalysis",
        "description": "Lab test for urine analysis.",
        "duration": 10,
        "price": 500.00,
    },
    {
        "name": "FBC (Full Blood Count)",
        "description": "Comprehensive blood test.",
        "duration": 10,
        "price": 1200.00,
    },
    {
        "name": "Referral Specialist Visit",
        "description": "Consultation with a specialist upon referral.",
        "duration": 30,
        "price": 2500.00,
    },
    {
        "name": "Emergency Consultation",
        "description": "Immediate consultation for urgent cases.",
        "duration": 20,
        "price": 1500.00,
    },
    {
        "name": "Vaccination",
        "description": "Administering vaccines as per schedule.",
        "duration": 15,
        "price": 1000.00,
    },
    {
        "name": "Health Education Session",
        "description": "Educational session on health topics.",
        "duration": 30,
        "price": 1200.00,
    },
    {
        "name": "Mental Health Counseling",
        "description": "Counseling session for mental health support.",
        "duration": 45,
        "price": 1800.00,
    },
    {
        "name": "Nutrition Consultation",
        "description": "Consultation with a nutritionist for dietary advice.",
        "duration": 30,
        "price": 1500.00,
    },
    {
        "name": "Family Planning Consultation",
        "description": "Consultation on family planning options.",
        "duration": 30,
        "price": 1200.00,
    },
]

class Command(BaseCommand):
    help = "Populate the Service table with important healthcare services"

    def handle(self, *args, **kwargs):
        for service in SERVICES:
            obj, created = Service.objects.get_or_create(
                name=service["name"],
                defaults={
                    "description": service["description"],
                    "duration": service["duration"],
                    "price": service["price"],
                    "is_active": True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added service: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Service already exists: {obj.name}"))
        self.stdout.write(self.style.SUCCESS("Service population complete."))