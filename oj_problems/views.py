from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Problem, TestCase
from .executor import CodeExecutor
from oj_submissions.models import Submission, Language, SubmissionStatus
from oj_users.models import User
from oj_judge.judge_queue import update_user_statistics
from django.core.paginator import Paginator
import json


def problem_list(request):
    difficulty = request.GET.get('difficulty', '')
    search_query = request.GET.get('search', '')
    
    problems = Problem.objects.filter(is_public=True)
    
    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    
    if search_query:
        problems = problems.filter(title__icontains=search_query)
    
    paginator = Paginator(problems, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    difficulties = ['Easy', 'Medium', 'Hard']
    
    return render(request, 'oj_problems/problem_list.html', {
        'page_obj': page_obj,
        'difficulties': difficulties,
        'current_difficulty': difficulty,
        'search_query': search_query,
    })


def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id, is_public=True)
    
    test_cases = problem.test_cases.all()
    
    return render(request, 'oj_problems/problem_detail.html', {
        'problem': problem,
        'test_cases': test_cases,
    })


def code_editor(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id, is_public=True)
    language = request.GET.get('language', 'python')
    
    return render(request, 'oj_problems/code_editor.html', {
        'problem': problem,
        'language': language,
    })


@csrf_exempt
def submit_code(request, problem_id):
    if request.method == 'POST':
        problem = get_object_or_404(Problem, id=problem_id)
        
        try:
            data = json.loads(request.body)
            is_ajax = True
        except:
            data = request.POST
            is_ajax = False
        
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        user = request.user if request.user.is_authenticated else None
        
        submission = Submission.objects.create(
            problem=problem,
            user=user,
            code=code,
            language=language,
            status=SubmissionStatus.PENDING,
        )
        
        executor = CodeExecutor(language)
        output, error, exec_time = executor.execute(code, '')
        
        if error:
            submission.status = SubmissionStatus.RUNTIME_ERROR
            submission.error_message = error
            submission.save()
        else:
            test_cases = problem.test_cases.filter(is_sample=True)
            all_passed = True
            
            for tc in test_cases:
                tc_output, tc_error, _ = executor.execute(code, tc.input_data)
                
                if tc_error or tc_output.strip() != tc.expected_output.strip():
                    all_passed = False
                    break
            
            if all_passed:
                submission.status = SubmissionStatus.ACCEPTED
            else:
                submission.status = SubmissionStatus.WRONG_ANSWER
            
            submission.save()
        
        if user:
            update_user_statistics(user)
        
        if is_ajax:
            redirect_url = f'/submissions/{submission.id}/'
            return JsonResponse({'success': True, 'redirect_url': redirect_url, 'status': submission.status})
        else:
            return redirect('submission_detail', submission_id=submission.id)
    
    return redirect('code_editor', problem_id=problem_id)


class ProblemAPI(View):
    def get(self, request):
        problems = Problem.objects.filter(is_public=True).values(
            'id', 'title', 'slug', 'difficulty', 'total_submissions',
            'accepted_submissions', 'acceptance_rate'
        )
        return JsonResponse({'problems': list(problems)})


class ProblemDetailAPI(View):
    def get(self, request, problem_id):
        problem = get_object_or_404(Problem, id=problem_id, is_public=True)
        data = {
            'id': problem.id,
            'title': problem.title,
            'description': problem.description,
            'input_description': problem.input_description,
            'output_description': problem.output_description,
            'sample_input': problem.sample_input,
            'sample_output': problem.sample_output,
            'hint': problem.hint,
            'difficulty': problem.difficulty,
            'time_limit': problem.time_limit,
            'memory_limit': problem.memory_limit
        }
        return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class RunCodeAPI(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except:
            data = request.POST
        
        code = data.get('code', '')
        language = data.get('language', 'python')
        input_data = data.get('input', '')
        
        executor = CodeExecutor(language)
        output, error, exec_time = executor.execute(code, input_data)
        
        if error:
            return JsonResponse({'success': False, 'error': error})
        else:
            return JsonResponse({'success': True, 'output': output, 'time': exec_time})
