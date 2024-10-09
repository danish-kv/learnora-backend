from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContestViewSet, QuestionViewSet, SubmissionViewSet, global_leaderboard

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'contest', ContestViewSet, basename='contest')
router.register(r'question', QuestionViewSet, basename='question')
router.register(r'answer-submission', SubmissionViewSet, basename='answer-submission')

urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs
    path('global-leaderboard/', global_leaderboard, name='global-leaderboard')  # Global leaderboard endpoint
]
