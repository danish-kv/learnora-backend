from django.urls import path, include
from .views import StudentManageView, RequestedCourses, RequestedCategory, AdminDashboardView, AdminSalesReport
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'requested-courses', RequestedCourses, basename='requested-course'),
router.register(r'requested-category', RequestedCategory, basename='requested-category'),
router.register(r'admin-dashboard', AdminDashboardView, basename='admin-dashboard'),
router.register(r'admin/sales-report', AdminSalesReport, basename='tutor-sales')


urlpatterns = [
    path('',include(router.urls)),
    path('students/', StudentManageView.as_view(), name='student' ),
    path('students/<int:id>', StudentManageView.as_view(), name='student-block' )
]
