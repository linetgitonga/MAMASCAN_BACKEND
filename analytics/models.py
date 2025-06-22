from django.db import models
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from appointments.models import Appointment, Client, Staff, Service
from django.conf import settings

class AnalyticsReport(models.Model):
    REPORT_TYPES = [
        ('appointments', 'Appointments Report'),
        ('revenue', 'Revenue Report'),
        ('staff_performance', 'Staff Performance'),
        ('client_analysis', 'Client Analysis'),
        ('service_popularity', 'Service Popularity'),
        ('feedback_summary', 'Feedback Summary'),
    ]
    
    name = models.CharField(max_length=100)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    date_from = models.DateField()
    date_to = models.DateField()
    generated_by = user = settings.AUTH_USER_MODEL
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict)
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        app_label = 'analytics'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"

class KPIMetric(models.Model):
    name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=20, blank=True)
    date = models.DateField()
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'analytics'
        unique_together = ['name', 'date', 'category']
    
    def __str__(self):
        return f"{self.name}: {self.value} {self.unit} ({self.date})"
