from django.urls import path, include
from .views import (
    CommunityCreateAPIView,
    ListCommunity,
    JoinCommunityAPIView,
    ChatHistoryAPIView,
    exit_community,
    NotificationViewSet
)
from rest_framework.routers import DefaultRouter

# Initialize the router for the API views
router = DefaultRouter()
router.register('list-community', ListCommunity, basename='list-community')
router.register('notification', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('create-community/', CommunityCreateAPIView.as_view(), name='community-create'),
    path('community/<slug:slug>/join/', JoinCommunityAPIView.as_view(), name='join-community'),
    path('community/<slug:slug>/chat/', ChatHistoryAPIView.as_view(), name='chat-history'),
    path('community/<slug:slug>/exit/', exit_community, name='exit-community')
]
