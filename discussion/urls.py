from django.urls import path, include
from .views import create_discussion, DiscussionViewSet, CommentViewSet
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()
routers.register(r'discussion', DiscussionViewSet, basename='discussion')
routers.register(r'comment', CommentViewSet, basename='comment')


urlpatterns = [
    path('', include(routers.urls)),
    path('create-discussion/', create_discussion, name='create-discussion'),

]
