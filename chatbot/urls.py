from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversactionViewSet

routers = DefaultRouter()
routers.register(r'conversations', ConversactionViewSet, basename='conversations')

urlpatterns = [
    path('', include(routers.urls))    
]

