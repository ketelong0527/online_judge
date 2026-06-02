from django.urls import path
from . import views

urlpatterns = [
    path('', views.submission_list, name='submission_list'),
    path('<int:submission_id>/', views.submission_detail, name='submission_detail'),
    
    path('api/', views.SubmissionAPI.as_view(), name='submission_api'),
    path('api/<int:submission_id>/', views.SubmissionDetailAPI.as_view(), name='submission_detail_api'),
]
