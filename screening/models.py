# screening/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
# User = get_user_model()
from accounts.models import User  # Ensure this import matches your User model location

class Patient(models.Model):
    # Personal Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    national_id = models.CharField(max_length=20, unique=True)
    
    # Location
    county = models.CharField(max_length=100)
    sub_county = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    
    # Medical Information
    marital_status = models.CharField(max_length=20, choices=[
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ])
    
    # Registered by
    registered_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='registered_patients',
        default=1
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        from datetime import date
        return (date.today() - self.date_of_birth).days // 365
    
    class Meta:
        db_table = 'screening_patient'

class ScreeningRecord(models.Model):
    RISK_LEVELS = [
        ('LOW', 'Low Risk'),
        ('MODERATE', 'Moderate Risk'),
        ('HIGH', 'High Risk'),
    ]
    
    BETHESDA_CATEGORIES = [
        ('NILM', 'Negative for Intraepithelial Lesion or Malignancy'),
        ('ASCUS', 'Atypical Squamous Cells of Undetermined Significance'),
        ('LSIL', 'Low-grade Squamous Intraepithelial Lesion'),
        ('HSIL', 'High-grade Squamous Intraepithelial Lesion'),
        ('AGC', 'Atypical Glandular Cells'),
        ('CANCER', 'Squamous Cell Carcinoma'),
    ]
    
    # Patient and Screening Info
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='screening_records')
    screened_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='screenings_conducted')
    screening_date = models.DateTimeField(auto_now_add=True)
    
    # Risk Factors
    age_at_first_intercourse = models.PositiveIntegerField(
        validators=[MinValueValidator(10), MaxValueValidator(50)],
        help_text="Age when first had sexual intercourse"
    )
    number_of_sexual_partners = models.PositiveIntegerField(default=1)
    parity = models.PositiveIntegerField(default=0, help_text="Number of pregnancies")
    
    # Medical History
    hiv_status = models.CharField(max_length=20, choices=[
        ('POSITIVE', 'Positive'),
        ('NEGATIVE', 'Negative'),
        ('UNKNOWN', 'Unknown'),
    ])
    
    hpv_vaccination_status = models.CharField(max_length=20, choices=[
        ('VACCINATED', 'Vaccinated'),
        ('NOT_VACCINATED', 'Not Vaccinated'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')
    
    contraceptive_use = models.CharField(max_length=30, choices=[
        ('NONE', 'None'),
        ('ORAL_PILLS', 'Oral Contraceptive Pills'),
        ('INJECTION', 'Injectable Contraceptives'),
        ('IUD', 'Intrauterine Device'),
        ('BARRIER', 'Barrier Methods'),
        ('OTHER', 'Other'),
    ], default='NONE')
    
    smoking_status = models.CharField(max_length=20, choices=[
        ('NEVER', 'Never'),
        ('FORMER', 'Former Smoker'),
        ('CURRENT', 'Current Smoker'),
    ], default='NEVER')
    
    family_history_cervical_cancer = models.BooleanField(default=False)
    previous_abnormal_pap = models.BooleanField(default=False)
    last_screening_date = models.DateField(null=True, blank=True)
    
    # Clinical Examination
    via_result = models.CharField(max_length=20, choices=[
        ('NEGATIVE', 'Negative'),
        ('POSITIVE', 'Positive'),
        ('SUSPICIOUS', 'Suspicious for Cancer'),
    ], blank=True, null=True)
    
    # Cytology Results
    bethesda_category = models.CharField(
        max_length=20, 
        choices=BETHESDA_CATEGORIES, 
        blank=True, 
        null=True
    )
    cytology_image = models.ImageField(upload_to='cytology_images/', blank=True, null=True)
    
    # AI Prediction Results
    ai_risk_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI-generated risk score between 0 and 1"
    )
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    ai_confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI model confidence in prediction"
    )
    
    # Recommendations
    recommended_action = models.TextField()
    follow_up_date = models.DateField(null=True, blank=True)
    referral_needed = models.BooleanField(default=False)
    referral_facility = models.CharField(max_length=200, blank=True)
    
    # Additional Notes
    clinical_notes = models.TextField(blank=True)
    offline_sync_status = models.BooleanField(default=False, help_text="True if synced from offline")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Screening for {self.patient} on {self.screening_date.date()}"
    
    class Meta:
        db_table = 'screening_screeningrecord'
        ordering = ['-screening_date']

class RiskFactorWeight(models.Model):
    """Model to store AI model feature weights for transparency"""
    factor_name = models.CharField(max_length=100, unique=True)
    weight = models.FloatField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.factor_name}: {self.weight}"
    
    class Meta:
        db_table = 'screening_riskfactorweight'

class ScreeningFollowUp(models.Model):
    FOLLOW_UP_STATUS = [
        ('PENDING', 'Pending'),
        ('CONTACTED', 'Patient Contacted'),
        ('COMPLETED', 'Follow-up Completed'),
        ('MISSED', 'Missed Appointment'),
        ('LOST', 'Lost to Follow-up'),
    ]
    
    screening_record = models.ForeignKey(
        ScreeningRecord, 
        on_delete=models.CASCADE, 
        related_name='follow_ups'
    )
    follow_up_date = models.DateField()
    status = models.CharField(max_length=20, choices=FOLLOW_UP_STATUS, default='PENDING')
    notes = models.TextField(blank=True)
    contacted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='follow_ups_conducted'
    )
    contact_method = models.CharField(max_length=20, choices=[
        ('PHONE', 'Phone Call'),
        ('SMS', 'SMS'),
        ('EMAIL', 'Email'),
        ('HOME_VISIT', 'Home Visit'),
        ('CLINIC_VISIT', 'Clinic Visit'),
    ], blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Follow-up for {self.screening_record.patient} on {self.follow_up_date}"
    
    class Meta:
        db_table = 'screening_screeningfollowup'
        ordering = ['-follow_up_date']