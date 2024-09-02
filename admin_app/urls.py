from django.urls import path, include
from .views import StudnetManageView, RequestedCourses
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'requested-courses', RequestedCourses, basename='requested-course'),


urlpatterns = [
    path('',include(router.urls)),
    path('students/', StudnetManageView.as_view(), name='student' ),
    path('students/<int:id>', StudnetManageView.as_view(), name='student-block' )
]
