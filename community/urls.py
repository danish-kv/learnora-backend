from django.urls import path, include
from .views import CommunityCreateAPIView, ListCommunity, JoinCommunityAPIView, ChatHistoryAPIView, exit_community
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(f'list-community', ListCommunity, basename='list-community')

urlpatterns = [
    path('', include(router.urls)),
    path('create-community/', CommunityCreateAPIView.as_view(), name='community-create' ),
    path('community/<slug:slug>/join/', JoinCommunityAPIView.as_view(), name='join-community'),
    path("community/<slug:slug>/chat/", ChatHistoryAPIView.as_view(), name='chat-history'),
    path('community/<slug:slug>/exit/', exit_community, name='exit-community')
]