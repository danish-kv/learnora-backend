from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentManageView,
    RequestedCourses,
    RequestedCategory,
    AdminDashboardView,
    AdminSalesReport,
)

# Initialize the DefaultRouter for registering viewsets
router = DefaultRouter()

# Registering ViewSets with the router
router.register(r'requested-courses', RequestedCourses, basename='requested-course')
router.register(r'requested-category', RequestedCategory, basename='requested-category')
router.register(r'admin-dashboard', AdminDashboardView, basename='admin-dashboard')
router.register(r'admin/sales-report', AdminSalesReport, basename='tutor-sales')

# Define URL patterns for the admin app
urlpatterns = [
    # Include the router's URLs
    path('', include(router.urls)),
    
    # Endpoint for managing students (list, block/unblock)
    path('students/', StudentManageView.as_view(), name='student-list'),
    path('students/<int:id>', StudentManageView.as_view(), name='student-block'),
]
