from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import create_discussion, DiscussionViewSet, CommentViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'discussion', DiscussionViewSet, basename='discussion')
router.register(r'comment', CommentViewSet, basename='comment')

# Define the URL patterns
urlpatterns = [
    # Include router URLs (for discussion and comment viewsets)
    path('', include(router.urls)),

    # Separate URL for creating a discussion via the custom API view
    path('create-discussion/', create_discussion, name='create-discussion'),
]
