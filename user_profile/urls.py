from django.urls import path
from .views import TutorProfile, TutorDetails

urlpatterns = [
    path('tutor/', TutorProfile.as_view(), name='tutor'),
    path('tutor/<str:pk>/', TutorDetails.as_view(), name='tutor-detail'),

]
