from django.db import models
from django.conf import settings


class Language(models.TextChoices):
    PYTHON = 'python', 'Python 3'
    JAVA = 'java', 'Java'
    CPP = 'cpp', 'C++'
    C = 'c', 'C'
    JAVASCRIPT = 'javascript', 'JavaScript'
    GO = 'go', 'Go'
    RUST = 'rust', 'Rust'


class SubmissionStatus(models.TextChoices):
    PENDING = 'Pending', '等待判题'
    JUDGING = 'Judging', '正在判题'
    ACCEPTED = 'Accepted', '答案正确'
    WRONG_ANSWER = 'Wrong Answer', '答案错误'
    TIME_LIMIT_EXCEEDED = 'Time Limit Exceeded', '超时'
    MEMORY_LIMIT_EXCEEDED = 'Memory Limit Exceeded', '内存超限'
    RUNTIME_ERROR = 'Runtime Error', '运行时错误'
    COMPILE_ERROR = 'Compile Error', '编译错误'
    SYSTEM_ERROR = 'System Error', '系统错误'


class Submission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='提交用户',
        null=True,
        blank=True
    )
    problem = models.ForeignKey(
        'oj_problems.Problem',
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='所属题目'
    )
    code = models.TextField('代码内容')
    language = models.CharField(
        '编程语言',
        max_length=20,
        choices=Language.choices,
        default=Language.PYTHON
    )
    status = models.CharField(
        '判题状态',
        max_length=30,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.PENDING
    )
    execution_time = models.IntegerField('运行时间(ms)', null=True, blank=True)
    execution_memory = models.IntegerField('内存占用(KB)', null=True, blank=True)
    error_message = models.TextField('错误信息', blank=True)
    score = models.IntegerField('得分', default=0)
    submitted_at = models.DateTimeField('提交时间', auto_now_add=True)
    judged_at = models.DateTimeField('判题完成时间', null=True, blank=True)
    is_public = models.BooleanField('是否公开', default=True)

    class Meta:
        verbose_name = '提交记录'
        verbose_name_plural = '提交记录列表'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {self.status}"


class SubmissionTestResult(models.Model):
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name='所属提交'
    )
    test_case = models.ForeignKey(
        'oj_problems.TestCase',
        on_delete=models.CASCADE,
        verbose_name='测试用例'
    )
    status = models.CharField(
        '状态',
        max_length=30,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.PENDING
    )
    actual_output = models.TextField('实际输出', blank=True)
    execution_time = models.IntegerField('运行时间(ms)', null=True, blank=True)
    execution_memory = models.IntegerField('内存占用(KB)', null=True, blank=True)
    is_passed = models.BooleanField('是否通过', default=False)

    class Meta:
        verbose_name = '测试结果'
        verbose_name_plural = '测试结果列表'
        ordering = ['test_case__order']

    def __str__(self):
        return f"{self.submission} - 测试{self.test_case.id} - {'通过' if self.is_passed else '失败'}"
