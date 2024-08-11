from django.urls import path
from .views import TutorProfile

urlpatterns = [
    path('tutor/', TutorProfile.as_view(), name='tutor')
]
