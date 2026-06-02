import threading
import queue
import time
from datetime import datetime
from django.utils import timezone
from .models import JudgeTask, JudgeStatus, JudgeResult, TestCaseResult, JudgeStatistics
from oj_problems.executor import CodeJudge


class JudgeQueue:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.queue = queue.PriorityQueue()
        self.running = False
        self.worker_thread = None
        self.current_task = None
    
    def start(self):
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()
            print(f"[JudgeQueue] Started at {datetime.now()}")
    
    def stop(self):
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        print(f"[JudgeQueue] Stopped at {datetime.now()}")
    
    def add_task(self, judge_task):
        priority = judge_task.priority
        self.queue.put((priority, judge_task.id, judge_task))
        print(f"[JudgeQueue] Task {judge_task.id} added with priority {priority}")
    
    def _worker(self):
        while self.running:
            try:
                priority, task_id, task = self.queue.get(timeout=1)
                
                if task.status == JudgeStatus.PENDING:
                    self.current_task = task
                    print(f"[JudgeQueue] Processing task {task_id}")
                    process_judge_task(task)
                    self.current_task = None
                
                self.queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[JudgeQueue] Error: {e}")
                self.current_task = None
    
    def get_queue_size(self):
        return self.queue.qsize()
    
    def get_status(self):
        return {
            'running': self.running,
            'queue_size': self.get_queue_size(),
            'current_task_id': self.current_task.id if self.current_task else None
        }


judge_queue = JudgeQueue()


def process_judge_task(judge_task):
    submission = judge_task.submission
    problem = submission.problem
    
    try:
        judge_task.mark_as_judging()
        
        judge_task.total_test_cases = problem.test_cases.count()
        judge_task.save()
        
        test_cases = problem.test_cases.all().order_by('order')
        judge = CodeJudge(submission.language)
        
        test_case_list = [
            {
                'id': tc.id,
                'input': tc.input_data,
                'output': tc.expected_output,
                'score': tc.score,
                'is_sample': tc.is_sample
            }
            for tc in test_cases
        ]
        
        result = judge.judge_submission(submission.code, test_case_list)
        
        judge_task.total_score = result['total_score']
        judge_task.max_score = result['max_score']
        
        execution_times = []
        execution_memories = []
        passed_count = 0
        
        TestCaseResult.objects.filter(judge_task=judge_task).delete()
        
        for i, tc_result in enumerate(result['results']):
            tc = test_cases[i]
            
            is_passed = tc_result['status'] == 'Accepted'
            if is_passed:
                passed_count += 1
            
            if 'execution_time' in tc_result:
                execution_times.append(tc_result['execution_time'])
            
            test_case_result = TestCaseResult.objects.create(
                judge_task=judge_task,
                test_case=tc,
                status=tc_result['status'],
                result=JudgeResult.PASSED if is_passed else JudgeResult.FAILED,
                score=tc_result.get('score', 0),
                execution_time=tc_result.get('execution_time', 0),
                actual_output=tc_result.get('output', ''),
                expected_output=tc.expected_output,
                input_data=tc.input_data,
                error_message=tc_result.get('error', ''),
                is_sample=tc.is_sample,
                order=tc.order
            )
        
        judge_task.passed_test_cases = passed_count
        
        if execution_times:
            judge_task.total_execution_time = sum(execution_times)
            judge_task.max_execution_time = max(execution_times)
            judge_task.min_execution_time = min(execution_times)
        
        if result['status'] == 'Accepted':
            judge_task.mark_as_completed(JudgeStatus.ACCEPTED)
        elif 'Time Limit' in result.get('status', ''):
            judge_task.mark_as_completed(JudgeStatus.TIME_LIMIT_EXCEEDED)
        elif 'Runtime' in result.get('status', ''):
            judge_task.mark_as_completed(JudgeStatus.RUNTIME_ERROR)
        else:
            judge_task.mark_as_completed(JudgeStatus.WRONG_ANSWER)
        
        submission.status = judge_task.status
        submission.score = judge_task.total_score
        submission.execution_time = judge_task.max_execution_time
        submission.save()
        
        update_user_statistics(submission.user)
        update_problem_statistics(problem)
        update_daily_statistics()
        
        print(f"[JudgeQueue] Task {judge_task.id} completed: {judge_task.status}")
        
    except Exception as e:
        error_msg = f"System error: {str(e)}"
        judge_task.retry_count += 1
        
        if judge_task.retry_count < judge_task.max_retries:
            judge_task.status = JudgeStatus.PENDING
            judge_task.error_message = error_msg
            judge_task.save()
            judge_queue.add_task(judge_task)
            print(f"[JudgeQueue] Task {judge_task.id} retry {judge_task.retry_count}/{judge_task.max_retries}")
        else:
            judge_task.mark_as_completed(JudgeStatus.SYSTEM_ERROR, error_message=error_msg)
            print(f"[JudgeQueue] Task {judge_task.id} failed: {error_msg}")


def judge_submission_async(submission):
    judge_task, created = JudgeTask.objects.get_or_create(
        submission=submission,
        defaults={'status': JudgeStatus.PENDING}
    )
    
    if created or judge_task.status in [JudgeStatus.PENDING, JudgeStatus.SYSTEM_ERROR]:
        judge_queue.add_task(judge_task)
        print(f"[JudgeQueue] Submission {submission.id} queued for judging")
    else:
        print(f"[JudgeQueue] Submission {submission.id} already being judged or completed")
    
    return judge_task


def update_user_statistics(user):
    from oj_submissions.models import Submission, SubmissionStatus
    
    user.total_submissions = Submission.objects.filter(user=user).count()
    user.accepted_submissions = Submission.objects.filter(
        user=user,
        status=SubmissionStatus.ACCEPTED
    ).count()
    
    user.total_solved = Submission.objects.filter(
        user=user,
        status=SubmissionStatus.ACCEPTED
    ).values('problem').distinct().count()
    
    user.save()


def update_problem_statistics(problem):
    from oj_submissions.models import Submission, SubmissionStatus
    
    problem.total_submissions = Submission.objects.filter(problem=problem).count()
    problem.accepted_submissions = Submission.objects.filter(
        problem=problem,
        status=SubmissionStatus.ACCEPTED
    ).count()
    
    if problem.total_submissions > 0:
        problem.acceptance_rate = (problem.accepted_submissions / problem.total_submissions) * 100
    else:
        problem.acceptance_rate = 0
    
    problem.save()


def update_daily_statistics():
    from oj_submissions.models import Submission, SubmissionStatus
    from django.db.models import Avg
    
    today = timezone.now().date()
    
    submissions_today = Submission.objects.filter(
        submitted_at__date=today
    )
    
    stats, created = JudgeStatistics.objects.get_or_create(date=today)
    
    stats.total_submissions = submissions_today.count()
    stats.accepted_submissions = submissions_today.filter(
        status=SubmissionStatus.ACCEPTED
    ).count()
    
    stats.save()


def get_judge_status(submission):
    try:
        judge_task = JudgeTask.objects.get(submission=submission)
        return {
            'task_id': judge_task.id,
            'status': judge_task.status,
            'total_score': judge_task.total_score,
            'max_score': judge_task.max_score,
            'passed_test_cases': judge_task.passed_test_cases,
            'total_test_cases': judge_task.total_test_cases,
            'is_completed': judge_task.is_completed,
            'created_at': judge_task.created_at,
            'started_at': judge_task.started_at,
            'completed_at': judge_task.completed_at,
            'error_message': judge_task.error_message
        }
    except JudgeTask.DoesNotExist:
        return None
