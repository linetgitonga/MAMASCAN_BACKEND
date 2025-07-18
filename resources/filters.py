import django_filters
from .models import Resource

class ResourceFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    min_duration = django_filters.NumberFilter(field_name='duration', lookup_expr='gte')
    max_duration = django_filters.NumberFilter(field_name='duration', lookup_expr='lte')
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    
    class Meta:
        model = Resource
        fields = ['type', 'difficulty', 'category', 'downloadable', 'instructor']
