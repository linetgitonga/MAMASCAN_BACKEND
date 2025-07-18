# resources/serializers.py
from rest_framework import serializers
from .models import Resource, UserProgress, ResourceRating, LearningPath

class ResourceSerializer(serializers.ModelSerializer):
    enrollments = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'description', 'type', 'duration', 'difficulty',
            'category', 'instructor', 'rating', 'downloadable', 'created_at',
            'updated_at', 'enrollments', 'average_rating', 'user_progress',
            'thumbnail', 'video_file', 'document_file'
        ]
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserProgress.objects.get(user=request.user, resource=obj)
                return {
                    'progress': progress.progress,
                    'completed': progress.completed,
                    'started_at': progress.started_at,
                    'completed_at': progress.completed_at,
                    'time_spent': progress.time_spent
                }
            except UserProgress.DoesNotExist:
                return None
        return None


class UserProgressSerializer(serializers.ModelSerializer):
    resource_title = serializers.CharField(source='resource.title', read_only=True)
    resource_type = serializers.CharField(source='resource.type', read_only=True)
    resource_difficulty = serializers.CharField(source='resource.difficulty', read_only=True)
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'resource', 'resource_title', 'resource_type', 'resource_difficulty',
            'progress', 'completed', 'started_at', 'completed_at', 'last_accessed',
            'time_spent'
        ]
        read_only_fields = ['started_at', 'completed_at', 'last_accessed']


class ResourceRatingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ResourceRating
        fields = ['id', 'user', 'user_name', 'resource', 'rating', 'review', 'created_at']
        read_only_fields = ['user', 'created_at']


class LearningPathSerializer(serializers.ModelSerializer):
    resources = ResourceSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = LearningPath
        fields = [
            'id', 'title', 'description', 'resources', 'created_by',
            'created_by_name', 'created_at', 'is_public'
        ]
        read_only_fields = ['created_by', 'created_at']