from django.contrib import admin
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'user_type', 'is_verified', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_verified', 'is_active')
    search_fields = ('email', 'username', 'phone_number', 'county', 'sub_county')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'years_of_experience', 'is_available_for_appointments', 'rating', 'total_ratings')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at',    'updated_at')