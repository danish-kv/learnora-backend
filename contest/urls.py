from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContestViewSet,QuestionViewSet

router = DefaultRouter()
router.register(r'contest', ContestViewSet, basename='contest')
router.register(r'question', QuestionViewSet, basename='question')


urlpatterns = [
    path('', include(router.urls)),
]
