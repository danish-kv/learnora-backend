from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet

routers = DefaultRouter()
routers.register(r'conversations', ConversationViewSet, basename='conversations')

urlpatterns = [
    path('', include(routers.urls))    
]

