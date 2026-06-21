"""
URL configuration for online_judge project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/problems/", permanent=True)),
    path("admin/", admin.site.urls),
    path("problems/", include('oj_problems.urls')),
    path("users/", include('oj_users.urls')),
    path("submissions/", include('oj_submissions.urls')),
]
