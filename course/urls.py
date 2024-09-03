from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, CategoryViewSet, ModuleView, EditModuleView, CoursePurchaseView, PaymentSuccess, ReviewViewSet, NotesViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'category', CategoryViewSet, basename='categroy')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'notes', NotesViewSet, basename='notes')


urlpatterns = [
    path('',include(router.urls)),
    path('modules/', ModuleView.as_view(), name='module'),
    path('modules/<pk>/', EditModuleView.as_view(), name='module-detail'),
    path('modules/<pk>/toggle-like/', EditModuleView.as_view(), name='module-toggle-like'),
    path('modules/<pk>/mark-watched/', EditModuleView.as_view(), name='mark-watched'),
    path('stripe/course-purchase', CoursePurchaseView.as_view(), name='stripe-payment'),
    path('payment_success/', PaymentSuccess.as_view(), name='payment-success'),
]
