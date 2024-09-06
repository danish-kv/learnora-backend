from django.shortcuts import render
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from .serializers import DiscussionSerializer, CommentSerializer
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .models import Discussion, Comment
from base.custom_permissions import IsStudent
# Create your views here.


class OncePerDayUserThrottle(UserRateThrottle):
    rate = '10/hour'


@api_view(['POST'])
# @throttle_classes([OncePerDayUserThrottle])
@permission_classes([IsStudent])
def create_discussion(request):
    if request.method == 'POST':
        user = request.user
        print('userrrrrrrr', user)

        data = request.data.copy()
        data['user'] = user.id
        serializer = DiscussionSerializer(data=data)

        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiscussionViewSet(ModelViewSet):
    queryset = Discussion.objects.all().prefetch_related('commented_discussion')
    serializer_class = DiscussionSerializer
    permission_classes = [IsStudent]


    def upvote(self, request, pk=None):
        discussion = self.get_object()
        discussion.upvote()
        return Response({'message' : 'Liked successfully', 'upvote_count' : discussion.upvote_count}, status=status.HTTP_200_OK)
    
    def downvote(self, request, pk=None):
        discussion = self.get_object()
        discussion.downvote()
        return Response({'message' : 'Unliked successfully', 'upvote_count' : discussion.upvote_count}, status=status.HTTP_200_OK)


class CommentViewSet(ModelViewSet):
    queryset = Comment
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        print(self.request.data)
        parent_id = self.request.data.get('parent', None)
        parent = None

        if parent_id:
            parent = Comment.objects.get(id=parent_id)
        serializer.save(user=self.request.user, parent=parent)


