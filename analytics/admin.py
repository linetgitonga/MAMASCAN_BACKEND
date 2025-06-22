from django.contrib import admin
from .models import AnalyticsReport, KPIMetric

@admin.register(AnalyticsReport)
class AnalyticsReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'date_from', 'date_to', 'generated_by', 'generated_at']
    list_filter = ['report_type', 'generated_at', 'is_scheduled']
    search_fields = ['name', 'description']
    readonly_fields = ['generated_at']

@admin.register(KPIMetric)
class KPIMetricAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'unit', 'category', 'date', 'created_at']
    list_filter = ['category', 'date', 'created_at']
    search_fields = ['name', 'category']