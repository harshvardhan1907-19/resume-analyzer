# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse  # Add this import

# Add this test view at the top
def test_api(request):
    return JsonResponse({"message": "API is working!", "status": "success"})

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin/', admin.site.urls),
    path('api/test/', test_api, name='test-api'),  # ← Add this line
    path('api/accounts/', include('accounts.urls')),
    path('api/resumes/', include('resumes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)