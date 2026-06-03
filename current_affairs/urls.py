from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyDigestViewSet

router = DefaultRouter()
router.register(r'', DailyDigestViewSet, basename='digest')

urlpatterns = [
    path('', include(router.urls)),
]