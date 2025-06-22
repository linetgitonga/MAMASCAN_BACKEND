# screening/serializers.py
from rest_framework import serializers
from .models import Patient, ScreeningRecord, ScreeningFollowUp, RiskFactorWeight
from accounts.serializers import UserSerializer

class PatientSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['registered_by']

class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ['registered_by']

class ScreeningRecordSerializer(serializers.ModelSerializer):
    patient_details = PatientSerializer(source='patient', read_only=True)
    screened_by_details = UserSerializer(source='screened_by', read_only=True)
    
    class Meta:
        model = ScreeningRecord
        fields = '__all__'
        read_only_fields = [
            'screened_by', 'ai_risk_score', 'risk_level', 
            'ai_confidence', 'recommended_action'
        ]

class ScreeningRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreeningRecord
        exclude = [
            'screened_by', 'ai_risk_score', 'risk_level', 
            'ai_confidence', 'recommended_action', 'screening_date'
        ]
    
    def validate(self, attrs):
        # Custom validation logic
        if attrs.get('age_at_first_intercourse', 0) > 30:
            raise serializers.ValidationError(
                "Age at first intercourse seems unusually high. Please verify."
            )
        
        if attrs.get('parity', 0) > 15:
            raise serializers.ValidationError(
                "Number of pregnancies seems unusually high. Please verify."
            )
        
        return attrs

class ScreeningFollowUpSerializer(serializers.ModelSerializer):
    contacted_by_details = UserSerializer(source='contacted_by', read_only=True)
    patient_name = serializers.CharField(
        source='screening_record.patient.first_name', 
        read_only=True
    )
    
    class Meta:
        model = ScreeningFollowUp
        fields = '__all__'
        read_only_fields = ['contacted_by']

class RiskFactorWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskFactorWeight
        fields = '__all__'

class RiskPredictionInputSerializer(serializers.Serializer):
    """Serializer for AI risk prediction input"""
    age = serializers.IntegerField(min_value=15, max_value=80)
    age_at_first_intercourse = serializers.IntegerField(min_value=10, max_value=50)
    number_of_sexual_partners = serializers.IntegerField(min_value=1, max_value=20)
    parity = serializers.IntegerField(min_value=0, max_value=15)
    hiv_status = serializers.ChoiceField(choices=['POSITIVE', 'NEGATIVE', 'UNKNOWN'])
    hpv_vaccination_status = serializers.ChoiceField(
        choices=['VACCINATED', 'NOT_VACCINATED', 'UNKNOWN']
    )
    contraceptive_use = serializers.ChoiceField(choices=[
        'NONE', 'ORAL_PILLS', 'INJECTION', 'IUD', 'BARRIER', 'OTHER'
    ])
    smoking_status = serializers.ChoiceField(choices=['NEVER', 'FORMER', 'CURRENT'])
    family_history_cervical_cancer = serializers.BooleanField()
    previous_abnormal_pap = serializers.BooleanField()
    via_result = serializers.ChoiceField(
        choices=['NEGATIVE', 'POSITIVE', 'SUSPICIOUS'], 
        required=False, 
        allow_null=True
    )
    bethesda_category = serializers.ChoiceField(
        choices=[
            'NILM', 'ASCUS', 'LSIL', 'HSIL', 'AGC', 'CANCER'
        ],
        required=False,
        allow_null=True
    )

class RiskPredictionOutputSerializer(serializers.Serializer):
    """Serializer for AI risk prediction output"""
    risk_score = serializers.FloatField()
    risk_level = serializers.CharField()
    confidence = serializers.FloatField()
    recommended_action = serializers.CharField()
    follow_up_months = serializers.IntegerField()
    referral_needed = serializers.BooleanField()
    explanation = serializers.ListField(child=serializers.CharField())

class ScreeningSummarySerializer(serializers.Serializer):
    """Serializer for screening statistics summary"""
    total_screenings = serializers.IntegerField()
    high_risk_count = serializers.IntegerField()
    moderate_risk_count = serializers.IntegerField()
    low_risk_count = serializers.IntegerField()
    referrals_made = serializers.IntegerField()
    follow_ups_pending = serializers.IntegerField()
    screenings_this_month = serializers.IntegerField()
    high_risk_percentage = serializers.FloatField()