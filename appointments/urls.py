from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/create/', views.appointment_create, name='appointment_create'),
    path('appointments/<uuid:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<uuid:pk>/update-status/', views.appointment_update_status, name='appointment_update_status'),
    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
]