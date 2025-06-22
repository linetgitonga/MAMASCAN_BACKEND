# accounts/views.py
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileSerializer, PasswordChangeSerializer, SpecialistListSerializer
)

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)

class SpecialistListView(generics.ListAPIView):
    serializer_class = SpecialistListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.filter(
            Q(user_type='SPECIALIST') | Q(user_type='CLINICIAN'),
            is_active=True,
            is_verified=True
        ).select_related('profile')
        
        # Filter by specialization if provided
        specialization = self.request.query_params.get('specialization')
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)
        
        # Filter by location
        county = self.request.query_params.get('county')
        if county:
            queryset = queryset.filter(county__icontains=county)
        
        # Filter by availability
        available_only = self.request.query_params.get('available_only', 'false')
        if available_only.lower() == 'true':
            queryset = queryset.filter(profile__is_available_for_appointments=True)
        
        return queryset

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats_view(request):
    user = request.user
    stats = {
        'total_screenings': 0,
        'high_risk_patients': 0,
        'appointments_completed': 0,
        'pending_appointments': 0,
    }
    
    if user.user_type in ['CHV', 'CLINICIAN']:
        from screening.models import ScreeningRecord
        from appointments.models import Appointment
        
        stats['total_screenings'] = ScreeningRecord.objects.filter(
            screened_by=user
        ).count()
        
        stats['high_risk_patients'] = ScreeningRecord.objects.filter(
            screened_by=user,
            risk_level='HIGH'
        ).count()
        
        stats['appointments_completed'] = Appointment.objects.filter(
            healthcare_provider=user,
            status='COMPLETED'
        ).count()
        
        stats['pending_appointments'] = Appointment.objects.filter(
            healthcare_provider=user,
            status='SCHEDULED'
        ).count()
    
    return Response(stats, status=status.HTTP_200_OK)