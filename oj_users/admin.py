from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'rating', 'rank',
                   'total_solved', 'acceptance_rate', 'is_active', 'created_at']
    list_filter = ['rank', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'school']
    readonly_fields = ['rating', 'total_solved', 'total_submissions',
                      'accepted_submissions', 'created_at', 'updated_at']

    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {
            'fields': ('avatar', 'bio', 'school', 'location', 'website',
                      'github_url', 'blog_url')
        }),
        ('用户统计', {
            'fields': ('rating', 'rank', 'total_solved', 'total_submissions',
                      'accepted_submissions', 'last_submission_time',
                      'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
