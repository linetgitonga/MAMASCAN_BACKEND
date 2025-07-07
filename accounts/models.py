# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    USER_TYPES = (
        ('CHV', 'Community Health Volunteer'),
        ('CLINICIAN', 'Clinician'),
        ('SPECIALIST', 'Specialist'),
        ('PATIENT', 'Patient'),
        ('ADMIN', 'Administrator'),
    )
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone_number = models.CharField(
        max_length=15, 
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True
    )
    county = models.CharField(max_length=100, blank=True)
    sub_county = models.CharField(max_length=100, blank=True)
    facility_name = models.CharField(max_length=200, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type']
    
    def __str__(self):
        return f"{self.email} - {self.get_user_type_display()}"
    
    class Meta:
        db_table = 'accounts_user'


from django.db.models.signals import post_save
from django.dispatch import receiver
from appointments.models import Client, Staff, Service  # adjust import if needed
from screening.models import Patient  # adjust import if needed
@receiver(post_save, sender=User)
def create_related_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'PATIENT':
            # Create Client if not exists
            Client.objects.get_or_create(
                user=instance,
                defaults={
                    "first_name": instance.first_name,
                    "last_name": instance.last_name,
                    "email": instance.email,
                    "phone": instance.phone_number,
                    "date_of_birth": instance.date_of_birth,
                }
            )
            Patient.objects.get_or_create(
                user=instance,
                defaults={
                    "first_name": instance.first_name,
                    "last_name": instance.last_name,
                    "date_of_birth": instance.date_of_birth,
                    "phone_number": instance.phone_number,
                    "email": instance.email,
                    "national_id": f"temp-{instance.pk}",  # Temporary unique national_id
                }
            )
        elif instance.user_type in ['CHV', 'CLINICIAN', 'SPECIALIST']:
            # Create Staff if not exists
            Staff.objects.get_or_create(
                user=instance,
                defaults={
                    "first_name": instance.first_name,
                    "last_name": instance.last_name,
                    "email": instance.email,
                    "phone": instance.phone_number,
                    "specialization": instance.specialization,
                    "hire_date": instance.created_at.date() if instance.created_at else None,
                }
            )




class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    languages_spoken = models.JSONField(default=list)
    availability_schedule = models.JSONField(default=dict)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.PositiveIntegerField(default=0)
    is_available_for_appointments = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile for {self.user.email}"
    
    class Meta:
        db_table = 'accounts_userprofile'