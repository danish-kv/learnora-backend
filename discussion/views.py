from django.shortcuts import render
from rest_framework.decorators import api_view, throttle_classes, permission_classes , action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from .serializers import DiscussionSerializer, CommentSerializer
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .models import Discussion, Comment
from base.custom_permissions import IsStudent
from rest_framework.permissions import AllowAny
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
        serializer = DiscussionSerializer(data=data, context={'request' : request})

        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiscussionViewSet(ModelViewSet):
    queryset = Discussion.objects.all().prefetch_related('user').prefetch_related('commented_discussion')
    serializer_class = DiscussionSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        discussion = self.get_object()
        user = request.user
        discussion.upvote(user)
        
        return Response({'message' : 'Liked successfully', 'upvote_count' : discussion.upvote_count}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def downvote(self, request, pk=None):
        discussion = self.get_object()
        user = request.user
        discussion.downvote(user)
        return Response({'message' : 'Unliked successfully', 'downvote_count' : discussion.downvote_count}, status=status.HTTP_200_OK)



    def update(self, request, *args, **kwargs):

        discussion = self.get_object()
        if discussion.user != request.user:
            return Response({'error' : 'You are not allowed to edit this'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        disucssion = self.get_object()
        if disucssion.user != request.user:
            return Response({'error' : 'you are not allowed to delete this post'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
    

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        print(self.request.data)
        parent_id = self.request.data.get('parent', None)
        parent = None

        if parent_id:
            parent = Comment.objects.get(id=parent_id)
        serializer.save(user=self.request.user, parent=parent)



    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        print(request.data)
        if comment.user != request.user:
            return Response({'error' : 'you are not allowed to edit this comment'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            return Response({'error' : ' You are not allowed to delete this comment'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

