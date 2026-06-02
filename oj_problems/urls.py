from django.urls import path
from . import views

urlpatterns = [
    path('', views.problem_list, name='problem_list'),
    path('<int:problem_id>/', views.problem_detail, name='problem_detail'),
    path('<int:problem_id>/edit/', views.code_editor, name='code_editor'),
    path('<int:problem_id>/submit/', views.submit_code, name='submit_code'),
    
    path('api/', views.ProblemAPI.as_view(), name='problem_api'),
    path('api/<int:problem_id>/', views.ProblemDetailAPI.as_view(), name='problem_detail_api'),
    path('api/run/', views.RunCodeAPI.as_view(), name='run_code_api'),
]
