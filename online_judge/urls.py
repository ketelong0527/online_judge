"""
URL configuration for online_judge project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("problems/", include('oj_problems.urls')),
    path("users/", include('oj_users.urls')),
    path("submissions/", include('oj_submissions.urls')),
]
