from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('<str:username>/', views.user_detail, name='user_detail'),
    
    path('api/', views.UserAPI.as_view(), name='user_api'),
    path('api/<str:username>/', views.UserDetailAPI.as_view(), name='user_detail_api'),
]
