from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import JudgeTask, TestCaseResult, JudgeStatistics
from .judge_queue import get_judge_status, judge_queue
import json


class JudgeStatusAPI(View):
    def get(self, request, submission_id):
        from oj_submissions.models import Submission
        try:
            submission = Submission.objects.get(id=submission_id)
            status = get_judge_status(submission)
            
            if status:
                return JsonResponse({'success': True, 'data': status})
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Judge task not found'
                })
        except Submission.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Submission not found'
            }, status=404)


class JudgeQueueAPI(View):
    def get(self, request):
        queue_status = judge_queue.get_status()
        
        pending_tasks = JudgeTask.objects.filter(
            status='Pending'
        ).count()
        
        judging_tasks = JudgeTask.objects.filter(
            status='Judging'
        ).count()
        
        return JsonResponse({
            'success': True,
            'data': {
                'queue_running': queue_status['running'],
                'queue_size': queue_status['queue_size'],
                'current_task_id': queue_status['current_task_id'],
                'pending_tasks': pending_tasks,
                'judging_tasks': judging_tasks
            }
        })


class TestCaseResultAPI(View):
    def get(self, request, submission_id):
        from oj_submissions.models import Submission
        try:
            submission = Submission.objects.get(id=submission_id)
            judge_task = submission.judge_task
            
            if not judge_task or not judge_task.is_completed:
                return JsonResponse({
                    'success': False,
                    'error': 'Judge not completed'
                })
            
            test_results = TestCaseResult.objects.filter(
                judge_task=judge_task
            ).values(
                'id', 'test_case__order', 'status', 'result', 'score',
                'execution_time', 'expected_output', 'actual_output',
                'is_sample', 'error_message'
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'test_results': list(test_results),
                    'summary': {
                        'total_score': judge_task.total_score,
                        'max_score': judge_task.max_score,
                        'passed': judge_task.passed_test_cases,
                        'total': judge_task.total_test_cases,
                        'max_time': judge_task.max_execution_time,
                        'avg_time': judge_task.total_execution_time // judge_task.total_test_cases if judge_task.total_test_cases else 0
                    }
                }
            })
        except Submission.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Submission not found'
            }, status=404)


class JudgeStatisticsAPI(View):
    def get(self, request):
        days = int(request.GET.get('days', 7))
        from datetime import timedelta
        from django.utils import timezone
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        stats = JudgeStatistics.objects.filter(
            date__range=[start_date, end_date]
        ).order_by('-date')
        
        data = []
        for stat in stats:
            data.append({
                'date': stat.date,
                'total_submissions': stat.total_submissions,
                'accepted_submissions': stat.accepted_submissions,
                'acceptance_rate': stat.acceptance_rate,
                'average_execution_time': stat.average_execution_time,
                'average_score': stat.average_score
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })


class RejudgeAPI(View):
    @method_decorator(login_required)
    def post(self, request, submission_id):
        from oj_submissions.models import Submission
        from django.contrib.admin.utils import model_ngettext
        
        try:
            submission = Submission.objects.get(id=submission_id)
            
            if not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'Permission denied'
                }, status=403)
            
            judge_task = submission.judge_task
            if judge_task:
                judge_task.status = 'Pending'
                judge_task.retry_count = 0
                judge_task.error_message = ''
                judge_task.save()
                judge_queue.add_task(judge_task)
            
            return JsonResponse({
                'success': True,
                'message': 'Rejudge requested'
            })
        except Submission.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Submission not found'
            }, status=404)
