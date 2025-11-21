from django.urls import path, include
from django.contrib import admin
from rest_framework import routers
from django.http import JsonResponse
from datetime import datetime

def health_check(request):
    """Health check endpoint pour Kubernetes"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'patient-service',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

router = routers.DefaultRouter()
# TODO: Register viewsets here
# router.register(r'patients', PatientViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health', health_check),
    path('api/', include(router.urls)),
]
