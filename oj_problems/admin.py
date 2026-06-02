from django.contrib import admin
from .models import Problem, TestCase


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'difficulty', 'total_submissions',
                    'accepted_submissions', 'acceptance_rate', 'is_public', 'created_at']
    list_filter = ['difficulty', 'is_public', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['total_submissions', 'accepted_submissions', 'created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'difficulty', 'is_public')
        }),
        ('题目内容', {
            'fields': ('description', 'input_description', 'output_description',
                      'sample_input', 'sample_output', 'hint')
        }),
        ('限制条件', {
            'fields': ('time_limit', 'memory_limit')
        }),
        ('统计信息', {
            'fields': ('total_submissions', 'accepted_submissions',
                      'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'problem', 'is_sample', 'score', 'order']
    list_filter = ['is_sample', 'problem']
    search_fields = ['problem__title']
    list_select_related = ['problem']
