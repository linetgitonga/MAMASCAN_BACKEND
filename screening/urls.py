from django.urls import path
from . import views

urlpatterns = [
    path('patients/', views.PatientListCreateView.as_view(), name='patient-list-create'),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name='patient-detail'),
    path('screenings/', views.ScreeningRecordListCreateView.as_view(), name='screeningrecord-list-create'),
    path('screenings/<int:pk>/', views.ScreeningRecordDetailView.as_view(), name='screeningrecord-detail'),
    path('followups/', views.ScreeningFollowUpListCreateView.as_view(), name='screeningfollowup-list-create'),
    # Add detail view for followups if needed
    path('predict-risk/', views.predict_risk_view, name='predict-risk'),
]