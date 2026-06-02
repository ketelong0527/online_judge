from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from .models import Submission, Language, SubmissionStatus
from django.core.paginator import Paginator


def submission_list(request):
    user_id = request.GET.get('user')
    problem_id = request.GET.get('problem')
    status = request.GET.get('status')
    language = request.GET.get('language')
    
    submissions = Submission.objects.select_related('user', 'problem')
    
    if user_id:
        submissions = submissions.filter(user_id=user_id)
    if problem_id:
        submissions = submissions.filter(problem_id=problem_id)
    if status:
        submissions = submissions.filter(status=status)
    if language:
        submissions = submissions.filter(language=language)
    
    paginator = Paginator(submissions, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'oj_submissions/submission_list.html', {
        'page_obj': page_obj,
        'status': status,
        'language': language,
        'user_id': user_id,
        'problem_id': problem_id,
        'status_choices': SubmissionStatus.choices,
        'language_choices': Language.choices
    })


def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    test_results = submission.test_results.all()
    
    return render(request, 'oj_submissions/submission_detail.html', {
        'submission': submission,
        'test_results': test_results
    })


class SubmissionAPI(View):
    def get(self, request):
        submissions = Submission.objects.select_related('user', 'problem').values(
            'id', 'user__username', 'problem__title', 'problem__id',
            'language', 'status', 'execution_time', 'execution_memory',
            'submitted_at'
        )[:50]
        return JsonResponse({'submissions': list(submissions)})


class SubmissionDetailAPI(View):
    def get(self, request, submission_id):
        submission = get_object_or_404(Submission, id=submission_id)
        test_results = submission.test_results.all().values(
            'test_case__id', 'status', 'is_passed', 'execution_time', 'actual_output'
        )
        data = {
            'id': submission.id,
            'user': submission.user.username,
            'problem': submission.problem.title,
            'problem_id': submission.problem.id,
            'code': submission.code,
            'language': submission.language,
            'status': submission.status,
            'execution_time': submission.execution_time,
            'execution_memory': submission.execution_memory,
            'error_message': submission.error_message,
            'score': submission.score,
            'submitted_at': submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            'test_results': list(test_results)
        }
        return JsonResponse(data)
