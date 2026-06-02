from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    bio = models.TextField('个人简介', max_length=500, blank=True)
    rating = models.IntegerField('积分', default=0)
    rank = models.CharField('段位', max_length=50, default='新手')
    total_solved = models.IntegerField('总解题数', default=0)
    total_submissions = models.IntegerField('总提交数', default=0)
    accepted_submissions = models.IntegerField('通过提交数', default=0)
    github_url = models.URLField('GitHub链接', blank=True)
    blog_url = models.URLField('博客链接', blank=True)
    school = models.CharField('学校/公司', max_length=200, blank=True)
    location = models.CharField('所在地', max_length=200, blank=True)
    website = models.URLField('个人网站', blank=True)
    last_submission_time = models.DateTimeField('最后提交时间', null=True, blank=True)
    created_at = models.DateTimeField('注册时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户列表'
        ordering = ['-rating']

    def __str__(self):
        return self.username

    @property
    def acceptance_rate(self):
        if self.get_total_submissions() == 0:
            return 0.0
        return round((self.get_accepted_submissions() / self.get_total_submissions()) * 100, 2)

    def update_stats(self):
        from oj_submissions.models import Submission, SubmissionStatus
        
        self.total_submissions = Submission.objects.filter(user=self).count()
        self.accepted_submissions = Submission.objects.filter(
            user=self,
            status=SubmissionStatus.ACCEPTED
        ).count()
        self.total_solved = Submission.objects.filter(
            user=self,
            status=SubmissionStatus.ACCEPTED
        ).values('problem').distinct().count()
        self.save()
    
    def get_total_submissions(self):
        from oj_submissions.models import Submission
        return Submission.objects.filter(user=self).count()
    
    def get_accepted_submissions(self):
        from oj_submissions.models import Submission, SubmissionStatus
        return Submission.objects.filter(
            user=self,
            status=SubmissionStatus.ACCEPTED
        ).count()
    
    def get_total_solved(self):
        from oj_submissions.models import Submission, SubmissionStatus
        return Submission.objects.filter(
            user=self,
            status=SubmissionStatus.ACCEPTED
        ).values('problem').distinct().count()
