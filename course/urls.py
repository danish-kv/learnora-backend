from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'category', CategoryViewSet, basename='categroy')

urlpatterns = router.urls

