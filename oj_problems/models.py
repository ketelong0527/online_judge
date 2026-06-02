from django.db import models


class DifficultyLevel(models.TextChoices):
    EASY = 'Easy', '简单'
    MEDIUM = 'Medium', '中等'
    HARD = 'Hard', '困难'


class Problem(models.Model):
    title = models.CharField('题目标题', max_length=200, unique=True)
    slug = models.SlugField('URL别名', max_length=200, unique=True)
    description = models.TextField('题目描述')
    input_description = models.TextField('输入描述')
    output_description = models.TextField('输出描述')
    sample_input = models.TextField('示例输入')
    sample_output = models.TextField('示例输出')
    hint = models.TextField('提示', blank=True, null=True)
    difficulty = models.CharField(
        '难度',
        max_length=10,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.MEDIUM
    )
    time_limit = models.IntegerField('时间限制(毫秒)', default=2000)
    memory_limit = models.IntegerField('内存限制(MB)', default=256)
    total_submissions = models.IntegerField('总提交数', default=0)
    accepted_submissions = models.IntegerField('通过数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_public = models.BooleanField('是否公开', default=True)

    class Meta:
        verbose_name = '题目'
        verbose_name_plural = '题目列表'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}. {self.title}"

    @property
    def acceptance_rate(self):
        if self.total_submissions == 0:
            return 0.0
        return round((self.accepted_submissions / self.total_submissions) * 100, 2)


class TestCase(models.Model):
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='test_cases',
        verbose_name='所属题目'
    )
    input_data = models.TextField('输入数据')
    expected_output = models.TextField('预期输出')
    is_sample = models.BooleanField('是否为示例', default=False)
    score = models.IntegerField('分值', default=10)
    order = models.IntegerField('执行顺序', default=0)

    class Meta:
        verbose_name = '测试用例'
        verbose_name_plural = '测试用例列表'
        ordering = ['order']

    def __str__(self):
        return f"{self.problem.title} - 测试用例 {self.id}"
