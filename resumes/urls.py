from django.urls import path
from .views import ResumeUploadView, ResumeListView, ResumeAnalyzeView

urlpatterns = [
    path('upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('analyze/', ResumeAnalyzeView.as_view(), name='resume-analyze'),
    path('', ResumeListView.as_view(), name='resume-list'),
]