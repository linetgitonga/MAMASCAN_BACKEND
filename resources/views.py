from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from .models import Resource, UserProgress, ResourceRating, LearningPath
from .serializers import (
    ResourceSerializer, UserProgressSerializer, 
    ResourceRatingSerializer, LearningPathSerializer
)


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.filter(is_active=True)
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'difficulty', 'category', 'downloadable']
    search_fields = ['title', 'description', 'instructor']
    ordering_fields = ['created_at', 'rating', 'title', 'duration']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by completion status for authenticated users
        completed_only = self.request.query_params.get('completed_only', None)
        if completed_only and self.request.user.is_authenticated:
            if completed_only.lower() == 'true':
                queryset = queryset.filter(
                    user_progress__user=self.request.user,
                    user_progress__completed=True
                )
            elif completed_only.lower() == 'false':
                queryset = queryset.filter(
                    Q(user_progress__user=self.request.user, user_progress__completed=False) |
                    ~Q(user_progress__user=self.request.user)
                )
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        resource = self.get_object()
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            resource=resource,
            defaults={'progress': 0}
        )
        
        if created:
            return Response(
                {'message': 'Successfully enrolled in resource'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Already enrolled in this resource'},
                status=status.HTTP_200_OK
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_progress(self, request, pk=None):
        resource = self.get_object()
        progress_value = request.data.get('progress', 0)
        time_spent = request.data.get('time_spent', 0)
        
        try:
            progress_obj = UserProgress.objects.get(user=request.user, resource=resource)
            progress_obj.progress = min(100, max(0, progress_value))
            progress_obj.time_spent += time_spent
            progress_obj.save()
            
            serializer = UserProgressSerializer(progress_obj)
            return Response(serializer.data)
        except UserProgress.DoesNotExist:
            return Response(
                {'error': 'Please enroll in the resource first'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        resource = self.get_object()
        rating_value = request.data.get('rating')
        review = request.data.get('review', '')
        
        rating, created = ResourceRating.objects.update_or_create(
            user=request.user,
            resource=resource,
            defaults={'rating': rating_value, 'review': review}
        )
        
        serializer = ResourceRatingSerializer(rating)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_resources(self, request):
        user_progress = UserProgress.objects.filter(user=request.user).select_related('resource')
        resources = [up.resource for up in user_progress]
        serializer = self.get_serializer(resources, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        return Response([{'value': choice[0], 'label': choice[1]} for choice in Resource.CATEGORY_CHOICES])
    
    @action(detail=False, methods=['get'])
    def difficulties(self, request):
        return Response([{'value': choice[0], 'label': choice[1]} for choice in Resource.DIFFICULTY_CHOICES])
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        return Response([{'value': choice[0], 'label': choice[1]} for choice in Resource.TYPE_CHOICES])


class UserProgressViewSet(viewsets.ModelViewSet):
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user).select_related('resource')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        progress_queryset = self.get_queryset()
        
        stats = {
            'total_enrolled': progress_queryset.count(),
            'completed': progress_queryset.filter(completed=True).count(),
            'in_progress': progress_queryset.filter(completed=False, progress__gt=0).count(),
            'not_started': progress_queryset.filter(progress=0).count(),
            'total_time_spent': sum(p.time_spent for p in progress_queryset),
            'average_progress': progress_queryset.aggregate(Avg('progress'))['progress__avg'] or 0,
        }
        
        return Response(stats)


class ResourceRatingViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceRatingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ResourceRating.objects.filter(user=self.request.user).select_related('resource')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LearningPathViewSet(viewsets.ModelViewSet):
    queryset = LearningPath.objects.all()
    serializer_class = LearningPathSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_public']
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(is_public=True) | Q(created_by=self.request.user)
            )
        return queryset.filter(is_public=True)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)