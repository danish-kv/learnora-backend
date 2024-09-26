from django.urls import path, include
from .views import TutorProfile, TutorDetails, MyProfileViewSets, SkillEditView, EducationEditView, ExperienceEditView, TutorDashboardView, TutorSalesReport
from rest_framework.routers import DefaultRouter 

router = DefaultRouter()
router.register(r'tutor-profile', MyProfileViewSets, basename='tutor-profile')
router.register(r'tutor-dashboard', TutorDashboardView, basename='tutor-dashboard')
router.register(r'tutor/sales-report', TutorSalesReport, basename='tutor-sales')

urlpatterns = [
    path('', include(router.urls)),
    path('tutor/', TutorProfile.as_view(), name='tutor'),
    path('tutor/<str:pk>/', TutorDetails.as_view(), name='tutor-detail'),
    path('tutor/skill/<str:id>/', SkillEditView.as_view(), name='tutor-skill'), 
    path('tutor/education/<str:id>/', EducationEditView.as_view(), name='tutor-skill'),
    path('tutor/experience/<int:id>/', ExperienceEditView.as_view(), name='tutor-skill'),
    # path('tutor/sales', TutorSalesReport.as_view(), name='tutor-sales'),

]
