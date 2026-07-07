from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyDigestViewSet, DailyQuizQuestionsView, DailyQuizSubmitView

router = DefaultRouter()
router.register(r'', DailyDigestViewSet, basename='digest')

urlpatterns = [
    path('daily-quiz/', DailyQuizQuestionsView.as_view(), name='daily-quiz-questions'),
    path('daily-quiz/submit/', DailyQuizSubmitView.as_view(), name='daily-quiz-submit'),
    path('', include(router.urls)),
]