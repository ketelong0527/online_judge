from django.contrib import admin
from .models import Submission, SubmissionTestResult


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'problem', 'language', 'status',
                   'execution_time', 'score', 'submitted_at']
    list_filter = ['status', 'language', 'submitted_at']
    search_fields = ['user__username', 'problem__title']
    readonly_fields = ['submitted_at', 'judged_at']
    raw_id_fields = ['user', 'problem']
    list_select_related = ['user', 'problem']

    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'problem', 'language', 'status', 'score')
        }),
        ('代码内容', {
            'fields': ('code',),
            'classes': ('collapse',)
        }),
        ('执行结果', {
            'fields': ('execution_time', 'execution_memory',
                      'error_message', 'judged_at')
        }),
        ('时间', {
            'fields': ('submitted_at', 'is_public'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SubmissionTestResult)
class SubmissionTestResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'submission', 'test_case', 'status',
                    'is_passed', 'execution_time']
    list_filter = ['status', 'is_passed']
    search_fields = ['submission__user__username', 'submission__problem__title']
    readonly_fields = ['execution_time', 'execution_memory']
    list_select_related = ['submission', 'test_case']
