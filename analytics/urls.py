from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('revenue/', views.revenue_analysis, name='revenue_analysis'),
    path('staff/', views.staff_performance, name='staff_performance'),
    path('clients/', views.client_analysis, name='client_analysis'),
    path('feedback/', views.feedback_analysis, name='feedback_analysis'),
    path('export/', views.export_report, name='export_report'),
]