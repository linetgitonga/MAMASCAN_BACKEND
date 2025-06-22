# screening/views.py
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Patient, ScreeningRecord, ScreeningFollowUp, RiskFactorWeight
from .serializers import (
    PatientSerializer, PatientCreateSerializer, ScreeningRecordSerializer,
    ScreeningRecordCreateSerializer, ScreeningFollowUpSerializer,
    RiskFactorWeightSerializer, RiskPredictionInputSerializer,
    RiskPredictionOutputSerializer, ScreeningSummarySerializer
)
from .ai_service import risk_predictor
import logging

logger = logging.getLogger(__name__)

class PatientListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PatientCreateSerializer
        return PatientSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Patient.objects.all()
        
        # Filter by user type
        if user.user_type in ['CHV', 'CLINICIAN']:
            queryset = queryset.filter(registered_by=user)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(national_id__icontains=search) |
                Q(phone_number__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)

class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type in ['CHV', 'CLINICIAN']:
            return Patient.objects.filter(registered_by=user)
        return Patient.objects.all()

class ScreeningRecordListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ScreeningRecordCreateSerializer
        return ScreeningRecordSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = ScreeningRecord.objects.select_related('patient', 'screened_by')
        
        # Filter by user type
        if user.user_type in ['CHV', 'CLINICIAN']:
            queryset = queryset.filter(screened_by=user)
        
        # Filter by patient
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Filter by risk level
        risk_level = self.request.query_params.get('risk_level')
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(screening_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(screening_date__lte=end_date)
        
        return queryset.order_by('-screening_date')
    
    def perform_create(self, serializer):
        # Get the validated data
        validated_data = serializer.validated_data
        
        # Prepare data for AI prediction
        patient = validated_data['patient']
        prediction_data = {
            'age': patient.age,
            'age_at_first_intercourse': validated_data['age_at_first_intercourse'],
            'number_of_sexual_partners': validated_data['number_of_sexual_partners'],
            'parity': validated_data['parity'],
            'hiv_status': validated_data['hiv_status'],
            'hpv_vaccination_status': validated_data['hpv_vaccination_status'],
            'contraceptive_use': validated_data['contraceptive_use'],
            'smoking_status': validated_data['smoking_status'],
            'family_history_cervical_cancer': validated_data['family_history_cervical_cancer'],
            'previous_abnormal_pap': validated_data['previous_abnormal_pap'],
            'via_result': validated_data.get('via_result'),
            'bethesda_category': validated_data.get('bethesda_category'),
        }
        
        # Get AI prediction
        try:
            prediction = risk_predictor.predict(prediction_data)
            
            # Save screening record with AI results
            screening_record = serializer.save(
                screened_by=self.request.user,
                ai_risk_score=prediction['risk_score'],
                risk_level=prediction['risk_level'],
                ai_confidence=prediction['confidence'],
                recommended_action=prediction['recommended_action'],
                referral_needed=prediction['referral_needed']
            )
            
            # Create follow-up if needed
            if prediction['follow_up_months'] <= 12:  # Create follow-up for <= 1 year
                follow_up_date = timezone.now().date() + timedelta(
                    days=prediction['follow_up_months'] * 30
                )
                ScreeningFollowUp.objects.create(
                    screening_record=screening_record,
                    follow_up_date=follow_up_date,
                    status='PENDING'
                )
            
            logger.info(f"Screening completed for patient {patient.id} with risk level {prediction['risk_level']}")
            
        except Exception as e:
            logger.error(f"Error in AI prediction: {e}")
            # Save with default values if AI prediction fails
            serializer.save(
                screened_by=self.request.user,
                ai_risk_score=0.5,
                risk_level='MODERATE',
                ai_confidence=0.5,
                recommended_action='Please consult healthcare provider for detailed assessment.',
                referral_needed=True
            )

class ScreeningRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ScreeningRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type in ['CHV', 'CLINICIAN']:
            return ScreeningRecord.objects.filter(screened_by=user)
        return ScreeningRecord.objects.all()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def predict_risk_view(request):
    """Standalone AI risk prediction endpoint"""
    serializer = RiskPredictionInputSerializer(data=request.data)
    if serializer.is_valid():
        try:
            prediction = risk_predictor.predict(serializer.validated_data)
            output_serializer = RiskPredictionOutputSerializer(prediction)
            return Response(output_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in risk prediction: {e}")
            return Response({
                'error': 'Risk prediction failed',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ScreeningFollowUpListCreateView(generics.ListCreateAPIView):
    serializer_class = ScreeningFollowUpSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = ScreeningFollowUp.objects.select_related(
            'screening_record__patient', 'contacted_by'
        )
        
        # Filter by user type
        if user.user_type in ['CHV', 'CLINICIAN']:
            queryset = queryset.filter(screening_record__screened_by=user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by due date
        overdue_only = self.request.query_params.get('overdue_only', 'false')
        if overdue_only.lower() == 'true':
            queryset = queryset.filter(
            follow_up_date__lt=timezone.now().date(),
            status='PENDING'
            )        