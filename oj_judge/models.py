from django.db import models
from django.conf import settings


class JudgeStatus(models.TextChoices):
    PENDING = 'Pending', '等待判题'
    JUDGING = 'Judging', '正在判题'
    ACCEPTED = 'Accepted', '答案正确'
    WRONG_ANSWER = 'Wrong Answer', '答案错误'
    TIME_LIMIT_EXCEEDED = 'Time Limit Exceeded', '超时'
    MEMORY_LIMIT_EXCEEDED = 'Memory Limit Exceeded', '内存超限'
    RUNTIME_ERROR = 'Runtime Error', '运行时错误'
    COMPILE_ERROR = 'Compile Error', '编译错误'
    SYSTEM_ERROR = 'System Error', '系统错误'


class JudgeResult(models.TextChoices):
    PASSED = 'Passed', '通过'
    FAILED = 'Failed', '失败'
    PARTIAL = 'Partial', '部分通过'


class JudgeTask(models.Model):
    submission = models.OneToOneField(
        'oj_submissions.Submission',
        on_delete=models.CASCADE,
        related_name='judge_task',
        verbose_name='提交记录'
    )
    
    status = models.CharField(
        '判题状态',
        max_length=30,
        choices=JudgeStatus.choices,
        default=JudgeStatus.PENDING
    )
    
    total_score = models.IntegerField('总得分', default=0)
    max_score = models.IntegerField('最高分', default=0)
    
    total_execution_time = models.IntegerField('总执行时间(ms)', null=True, blank=True)
    max_execution_time = models.IntegerField('最大执行时间(ms)', null=True, blank=True)
    min_execution_time = models.IntegerField('最小执行时间(ms)', null=True, blank=True)
    
    total_execution_memory = models.IntegerField('总内存占用(KB)', null=True, blank=True)
    max_execution_memory = models.IntegerField('最大内存占用(KB)', null=True, blank=True)
    
    passed_test_cases = models.IntegerField('通过的测试用例数', default=0)
    total_test_cases = models.IntegerField('总测试用例数', default=0)
    
    result_details = models.JSONField('详细结果', default=dict, blank=True)
    
    priority = models.IntegerField('优先级', default=0)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    
    retry_count = models.IntegerField('重试次数', default=0)
    max_retries = models.IntegerField('最大重试次数', default=3)
    
    error_message = models.TextField('错误信息', blank=True)
    
    judge_server = models.CharField('判题服务器', max_length=100, blank=True)
    
    class Meta:
        verbose_name = '判题任务'
        verbose_name_plural = '判题任务列表'
        ordering = ['-priority', 'created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['submission']),
        ]

    def __str__(self):
        return f"Task {self.id}: {self.submission} - {self.status}"

    @property
    def is_completed(self):
        return self.status not in [JudgeStatus.PENDING, JudgeStatus.JUDGING]

    @property
    def acceptance_rate(self):
        if self.total_test_cases == 0:
            return 0
        return (self.passed_test_cases / self.total_test_cases) * 100

    def update_status(self, status, **kwargs):
        self.status = status
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    def mark_as_judging(self):
        from django.utils import timezone
        self.status = JudgeStatus.JUDGING
        self.started_at = timezone.now()
        self.save()

    def mark_as_completed(self, status, **kwargs):
        from django.utils import timezone
        self.status = status
        self.completed_at = timezone.now()
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()


class TestCaseResult(models.Model):
    judge_task = models.ForeignKey(
        JudgeTask,
        on_delete=models.CASCADE,
        related_name='test_results'
    )
    
    test_case = models.ForeignKey(
        'oj_problems.TestCase',
        on_delete=models.CASCADE
    )
    
    status = models.CharField(
        '状态',
        max_length=30,
        choices=JudgeStatus.choices,
        default=JudgeStatus.PENDING
    )
    
    result = models.CharField(
        '结果',
        max_length=20,
        choices=JudgeResult.choices,
        default=JudgeResult.FAILED
    )
    
    score = models.IntegerField('得分', default=0)
    
    execution_time = models.IntegerField('执行时间(ms)', null=True, blank=True)
    execution_memory = models.IntegerField('内存占用(KB)', null=True, blank=True)
    
    expected_output = models.TextField('预期输出', blank=True)
    actual_output = models.TextField('实际输出', blank=True)
    
    input_data = models.TextField('输入数据', blank=True)
    
    error_message = models.TextField('错误信息', blank=True)
    
    is_sample = models.BooleanField('是否为示例', default=False)
    
    order = models.IntegerField('顺序', default=0)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '测试用例结果'
        verbose_name_plural = '测试用例结果列表'
        ordering = ['order']

    def __str__(self):
        return f"Result {self.id}: {self.test_case} - {self.result}"

    @property
    def is_passed(self):
        return self.result == JudgeResult.PASSED

    def compare_output(self):
        import difflib
        expected = self.expected_output.strip().replace('\r\n', '\n')
        actual = self.actual_output.strip().replace('\r\n', '\n')
        
        if expected == actual:
            return True, None
        
        diff = list(difflib.unified_diff(
            expected.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile='expected',
            tofile='actual',
            lineterm=''
        ))
        
        return False, ''.join(diff[:20])


class JudgeStatistics(models.Model):
    date = models.DateField('日期', unique=True)
    
    total_submissions = models.IntegerField('总提交数', default=0)
    accepted_submissions = models.IntegerField('通过数', default=0)
    
    average_execution_time = models.IntegerField('平均执行时间(ms)', default=0)
    average_score = models.IntegerField('平均得分', default=0)
    
    language_stats = models.JSONField('语言统计', default=dict)
    difficulty_stats = models.JSONField('难度统计', default=dict)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '判题统计'
        verbose_name_plural = '判题统计列表'
        ordering = ['-date']

    def __str__(self):
        return f"Stats {self.date}: {self.accepted_submissions}/{self.total_submissions}"

    @property
    def acceptance_rate(self):
        if self.total_submissions == 0:
            return 0
        return (self.accepted_submissions / self.total_submissions) * 100
