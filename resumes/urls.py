# resumes/urls.py
from django.urls import path
from django.http import JsonResponse
from .views import ResumeUploadView, ResumeListView, ResumeAnalyzeView

# Add this test view
def test_resumes(request):
    return JsonResponse({"message": "Resumes API is working!", "status": "success"})

urlpatterns = [
    path('test/', test_resumes, name='test-resumes'),  # ← Add this line
    path('upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('analyze/', ResumeAnalyzeView.as_view(), name='resume-analyze'),
    path('', ResumeListView.as_view(), name='resume-list'),
]