from django.urls import path
from . import views

app_name = 'oj_judge'

urlpatterns = [
    path('status/<int:submission_id>/', views.JudgeStatusAPI.as_view(), name='judge_status'),
    path('queue/', views.JudgeQueueAPI.as_view(), name='judge_queue'),
    path('results/<int:submission_id>/', views.TestCaseResultAPI.as_view(), name='test_results'),
    path('statistics/', views.JudgeStatisticsAPI.as_view(), name='statistics'),
    path('rejudge/<int:submission_id>/', views.RejudgeAPI.as_view(), name='rejudge'),
]
