from django.urls import path, include
from .views import CommunityCreateAPIView, ListCommunity
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(f'list-community', ListCommunity, basename='list-community')

urlpatterns = [
    path('', include(router.urls)),
    path('create-community/', CommunityCreateAPIView.as_view(), name='community-create' ),

]
