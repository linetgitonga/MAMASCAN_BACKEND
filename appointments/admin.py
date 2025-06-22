from django.contrib import admin
from .models import Service, Client, Staff, Appointment, AppointmentHistory, ClientFeedback

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    list_filter = ['created_at']

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'specialization', 'is_active', 'hire_date']
    list_filter = ['is_active', 'hire_date']
    search_fields = ['first_name', 'last_name', 'email']
    filter_horizontal = ['services']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['client', 'staff', 'service', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_date', 'service', 'staff']
    search_fields = ['client__first_name', 'client__last_name', 'staff__first_name', 'staff__last_name']
    date_hierarchy = 'appointment_date'
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(AppointmentHistory)
class AppointmentHistoryAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'previous_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['previous_status', 'new_status', 'changed_at']
    readonly_fields = ['changed_at']

@admin.register(ClientFeedback)
class ClientFeedbackAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'rating', 'would_recommend', 'created_at']
    list_filter = ['rating', 'would_recommend', 'created_at']
    readonly_fields = ['created_at']