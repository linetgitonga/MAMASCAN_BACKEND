# resources/admin.py
from django.contrib import admin
from .models import Resource, UserProgress, ResourceRating, LearningPath, LearningPathResource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'difficulty', 'category', 'instructor', 'rating', 'created_at']
    list_filter = ['type', 'difficulty', 'category', 'downloadable', 'created_at']
    search_fields = ['title', 'description', 'instructor']
    readonly_fields = ['created_at', 'updated_at', 'enrollments']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'instructor')
        }),
        ('Content Details', {
            'fields': ('type', 'duration', 'difficulty', 'category', 'downloadable')
        }),
        ('Files', {
            'fields': ('video_file', 'document_file', 'thumbnail')
        }),
        ('Metadata', {
            'fields': ('rating', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'progress', 'completed', 'last_accessed']
    list_filter = ['completed', 'resource__type', 'resource__difficulty', 'started_at']
    search_fields = ['user__username', 'resource__title']
    readonly_fields = ['started_at', 'completed_at', 'last_accessed']


@admin.register(ResourceRating)
class ResourceRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'resource__title']
    readonly_fields = ['created_at']


class LearningPathResourceInline(admin.TabularInline):
    model = LearningPathResource
    extra = 1


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']
    inlines = [LearningPathResourceInline]