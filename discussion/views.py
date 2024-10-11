from django.shortcuts import render
from rest_framework.decorators import api_view, throttle_classes, permission_classes, action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializers import DiscussionSerializer, CommentSerializer
from .models import Discussion, Comment
from base.custom_permissions import IsStudent



# Custom throttle rate limiting to 10 requests per hour
class OncePerDayUserThrottle(UserRateThrottle):
    rate = '10/hour'


@api_view(['POST'])
# @throttle_classes([OncePerDayUserThrottle])
@permission_classes([IsStudent])
def create_discussion(request):
    """
    API view to create a new discussion.
    Only accessible to users with the IsStudent permission.
    """
    if request.method == 'POST':
        user = request.user
        data = request.data.copy()
        data['user'] = user.id

        # Create discussion with validated data
        serializer = DiscussionSerializer(data=data, context={'request' : request})

        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiscussionViewSet(ModelViewSet):
    """
    ViewSet for managing discussions.
    Allows operations like upvoting, downvoting, updating, and deleting discussions.
    """
    queryset = Discussion.objects.all().prefetch_related('user', 'commented_discussion').order_by('-id')
    serializer_class = DiscussionSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        """
        Action to upvote a discussion by the current user.
        """
        discussion = self.get_object()
        user = request.user
        discussion.upvote(user)
        
        return Response({
            'message': 'Liked successfully', 
            'upvote_count': discussion.upvote_count
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def downvote(self, request, pk=None):
        """
        Action to downvote (unlike) a discussion by the current user.
        """
        discussion = self.get_object()
        user = request.user
        discussion.downvote(user)

        return Response({
            'message': 'Unliked successfully', 
            'downvote_count': discussion.downvote_count
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Update discussion. Only the user who created the discussion can update it.
        """
        discussion = self.get_object()

        if discussion.user != request.user:
            return Response({'error': 'You are not allowed to edit this'}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete discussion. Only the user who created the discussion can delete it.
        """
        discussion = self.get_object()

        if discussion.user != request.user:
            return Response({'error': 'You are not allowed to delete this post'}, status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)


class CommentViewSet(ModelViewSet):
    """
    ViewSet for managing comments on discussions.
    Includes logic for adding parent comments and user ownership validation for updates/deletion.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_serializer_context(self):
        """
        Provide extra context to the serializer.
        """
        return {'request': self.request}

    def perform_create(self, serializer):
        """
        Create a new comment, with optional parent comment support.
        """
        parent_id = self.request.data.get('parent', None)
        parent = None

        if parent_id:
            parent = Comment.objects.get(id=parent_id)

        serializer.save(user=self.request.user, parent=parent)

    def update(self, request, *args, **kwargs):
        """
        Update comment. Only the user who created the comment can update it.
        """
        comment = self.get_object()

        if comment.user != request.user:
            return Response({'error': 'You are not allowed to edit this comment'}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete comment. Only the user who created the comment can delete it.
        """
        comment = self.get_object()

        if comment.user != request.user:
            return Response({'error': 'You are not allowed to delete this comment'}, status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)