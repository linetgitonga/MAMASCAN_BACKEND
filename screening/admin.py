from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Patient, ScreeningRecord, RiskFactorWeight, ScreeningFollowUp

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'national_id', 'phone_number', 'county', 'sub_county', 'registered_by', 'created_at')
    search_fields = ('first_name', 'last_name', 'national_id', 'phone_number', 'email')
    list_filter = ('county', 'sub_county', 'marital_status')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ScreeningRecord)
class ScreeningRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'screened_by', 'screening_date', 'risk_level', 'ai_risk_score', 'ai_confidence', 'referral_needed')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__national_id')
    list_filter = ('risk_level', 'hiv_status', 'hpv_vaccination_status', 'contraceptive_use', 'smoking_status', 'referral_needed')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(RiskFactorWeight)
class RiskFactorWeightAdmin(admin.ModelAdmin):
    list_display = ('factor_name', 'weight', 'is_active')
    search_fields = ('factor_name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ScreeningFollowUp)
class ScreeningFollowUpAdmin(admin.ModelAdmin):
    list_display = ('screening_record', 'follow_up_date', 'status', 'contacted_by', 'contact_method')
    search_fields = ('screening_record__patient__first_name', 'screening_record__patient__last_name')
    list_filter = ('status', 'contact_method')
    readonly_fields = ('created_at', 'updated_at')