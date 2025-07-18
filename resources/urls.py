# resources/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResourceViewSet, UserProgressViewSet, ResourceRatingViewSet, LearningPathViewSet

router = DefaultRouter()
router.register(r'resources', ResourceViewSet)
router.register(r'progress', UserProgressViewSet, basename='progress')
router.register(r'ratings', ResourceRatingViewSet, basename='ratings')
router.register(r'learning-paths', LearningPathViewSet)

urlpatterns = [
    path('/', include(router.urls)),
]