from django.shortcuts import render, get_object_or_404
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny

from base.custom_permissions import IsTutor, IsStudent
from base.custom_pagination_class import CustomMessagePagination
from .models import Community, Message, Notification
from .serializer import (
    CommunitySerializer,
    MessageSerializer,
    CreateCommunitySerializer,
    JoinCommunitySerializer,
    NotificationSerializer
)


# Create your views here.

class CommunityCreateAPIView(generics.CreateAPIView):
    """
    API view to create a new community. Only tutors are allowed to create communities.
    """
    queryset = Community.objects.all()
    serializer_class = CreateCommunitySerializer
    permission_classes = [IsTutor]

    def perform_create(self, serializer):
        """
        Save the community instance with the associated tutor profile.
        """
        serializer.save(tutor=self.request.user.tutor_profile)


class ListCommunity(viewsets.ReadOnlyModelViewSet):
    """
    API view to list communities. Accessible to everyone.
    """
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Override to filter communities based on user role (tutor or student).
        """
        user = self.request.user
        queryset = Community.objects.all().order_by('-id')

        if user.is_anonymous or not user.is_authenticated:
            return queryset.all()
        elif hasattr(user, 'role'):
            if user.role == 'tutor':
                return queryset.filter(tutor__user=user)
            elif user.role == 'student':
                return queryset.all()

        return queryset


class JoinCommunityAPIView(APIView):
    """
    API view for users to join a community.
    """

    def post(self, request, slug):
        """
        Handle the POST request to join a community.
        """
        try:
            community = Community.objects.get(slug=slug)
        except Community.DoesNotExist:
            return Response({'error': 'Community not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user in community.participants.all():
            return Response({'error': 'Already a member; you can view the community.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = JoinCommunitySerializer(community, data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({'message': 'Successfully joined the community'}, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatHistoryAPIView(generics.ListAPIView):
    """
    API view to retrieve the chat history of a community.
    """
    serializer_class = MessageSerializer
    pagination_class = CustomMessagePagination

    def get_queryset(self):
        """
        Return the messages for the specified community.
        """
        slug = self.kwargs['slug']
        community = get_object_or_404(Community, slug=slug)
        return Message.objects.filter(community=community).order_by('created_at')


@api_view(['POST'])
def exit_community(request, slug):
    """
    API view to allow a user to exit a community.
    """
    community = get_object_or_404(Community, slug=slug)

    if request.user not in community.participants.all():
        return Response({'error': 'You are not a member of this community'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        community.exit_participant(request.user)
        return Response({'message': 'Successfully exited from community'}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing notifications for the authenticated user.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """
        Filter notifications to only those for the authenticated user.
        """
        return self.queryset.filter(recipient=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        """
        Mark a notification as read.
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'}, status=status.HTTP_200_OK)
