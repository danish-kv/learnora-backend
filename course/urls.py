from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, CategoryViewSet, ModuleView, ModuleView

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'category', CategoryViewSet, basename='categroy')


urlpatterns = [
    path('',include(router.urls)),
    path('modules/', ModuleView.as_view(), name='module'),
    path('modules/<pk>/', ModuleView.as_view(), name='module-delete')
]



