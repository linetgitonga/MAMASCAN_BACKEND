from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
import random

COUNTIES = ["Nairobi", "Mombasa", "Kisumu", "Kericho", "Nakuru", "Eldoret", "Machakos", "Nyeri", "Meru", "Kakamega"]
SPECIALIZATIONS = ["General", "Gynecology", "Oncology", "Pediatrics", "Radiology"]

# Sample African names
PATIENT_FIRST_NAMES = ["Amina", "Kwame", "Wanjiku", "Chinedu", "Fatou", "Thabo", "Zainab", "Kofi", "Lerato", "Abdi"]
PATIENT_LAST_NAMES = ["Odhiambo", "Njoroge", "Okeke", "Mensah", "Kamau", "Diallo", "Mugisha", "Mwangi", "Mutiso", "Ochieng"]

CHV_FIRST_NAMES = ["Mary", "John", "Grace", "James", "Sarah", "David"]
CHV_LAST_NAMES = ["Otieno", "Munyua", "Kagwe", "Wambua", "Karanja", "Omondi"]

CLINICIAN_FIRST_NAMES = ["Paul", "Mercy", "Samuel", "Joy", "Brian", "Alice"]
CLINICIAN_LAST_NAMES = ["Omondi", "Kiplagat", "Mugambi", "Wanjiru", "Karanja", "Muriuki"]

SPECIALIST_FIRST_NAMES = ["Esther", "Peter", "Linda", "David", "Joyce", "James"]
SPECIALIST_LAST_NAMES = ["Muriuki", "Okoth", "Munyiri", "Wambui", "Karanja", "Omondi"]

def random_phone():
    return f"+2547{random.randint(10000000, 99999999)}"

class Command(BaseCommand):
    help = "Populate the database with dummy users (patients, staff, etc.)"

    def handle(self, *args, **kwargs):
        # Create dummy patients
        for i in range(40):
            User.objects.create_user(
                email=f"patient{i}@example.com",
                username=f"patient{i}",
                password="testpass123",
                user_type="PATIENT",
                first_name=PATIENT_FIRST_NAMES[i % len(PATIENT_FIRST_NAMES)],
                last_name=PATIENT_LAST_NAMES[i % len(PATIENT_LAST_NAMES)],
                phone_number=random_phone(),
                county=random.choice(COUNTIES),
                date_of_birth=timezone.now().date().replace(year=1990 + i),
                is_verified=True,
            )

        # Create dummy CHVs
        for i in range(15):
            User.objects.create_user(
                email=f"chv{i}@example.com",
                username=f"chv{i}",
                password="testpass123",
                user_type="CHV",
                first_name=CHV_FIRST_NAMES[i % len(CHV_FIRST_NAMES)],
                last_name=CHV_LAST_NAMES[i % len(CHV_LAST_NAMES)],
                phone_number=random_phone(),
                county=random.choice(COUNTIES),
                specialization="General",
                is_verified=True,
            )

        # Create dummy clinicians
        for i in range(5):
            User.objects.create_user(
                email=f"clinician{i}@example.com",
                username=f"clinician{i}",
                password="testpass123",
                user_type="CLINICIAN",
                first_name=CLINICIAN_FIRST_NAMES[i % len(CLINICIAN_FIRST_NAMES)],
                last_name=CLINICIAN_LAST_NAMES[i % len(CLINICIAN_LAST_NAMES)],
                phone_number=random_phone(),
                county=random.choice(COUNTIES),
                specialization=random.choice(SPECIALIZATIONS),
                is_verified=True,
            )

        # Create dummy specialists
        for i in range(10):
            User.objects.create_user(
                email=f"specialist{i}@example.com",
                username=f"specialist{i}",
                password="testpass123",
                user_type="SPECIALIST",
                first_name=SPECIALIST_FIRST_NAMES[i % len(SPECIALIST_FIRST_NAMES)],
                last_name=SPECIALIST_LAST_NAMES[i % len(SPECIALIST_LAST_NAMES)],
                phone_number=random_phone(),
                county=random.choice(COUNTIES),
                specialization=random.choice(SPECIALIZATIONS),
                is_verified=True,
            )

        # Create an admin
        User.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="adminpass123",
            user_type="ADMIN",
            first_name="Admin",
            last_name="User",
            phone_number=random_phone(),
            county="Nairobi",
            is_verified=True,
        )

        self.stdout.write(self.style.SUCCESS("Dummy users created successfully!"))