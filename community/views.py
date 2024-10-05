from django.shortcuts import render
from .serializer import CommunitySerializer, MessageSerializer, CreateCommunitySerializer, JoinCommunitySerializer, NotificationSerializer
from .models import Community, Message, Notification
from rest_framework import status, generics, views
from rest_framework.response import Response
from base.custom_permissions import IsTutor, IsStudent
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from base.custom_pagination_class import CustomMessagePagination
from rest_framework.permissions import AllowAny
# Create your views here.



class CommunityCreateAPIView(generics.CreateAPIView):
    queryset = Community.objects.all()
    serializer_class = CreateCommunitySerializer
    permission_classes = [IsTutor]

    def perform_create(self, serializer):
        serializer.save(tutor = self.request.user.tutor_profile)




class ListCommunity(viewsets.ReadOnlyModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        queryset= Community.objects.all().order_by('-id')

        if user.is_anonymous or not user.is_authenticated:
            queryset = queryset.all()
        elif hasattr(user, 'role'):
            if user.role == 'tutor':
                queryset = queryset.filter(tutor__user=user)
            elif user.role == 'student':
                queryset = queryset.all()


        return queryset


class JoinCommunityAPIView(APIView):

    def post(self, request, slug):
        print('in community views ===')
        try:
            community = Community.objects.get(slug=slug)
            print('got community instance ==',community)
        except Community.DoesNotExist:
            return Response({'error' : 'Community not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user in community.participants.all():
            return Response({'error' : 'Already a memeber, You can view'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = JoinCommunitySerializer(community, data=request.data, context={'request' : request})
        if serializer.is_valid():
            print('serialzer is valid')
            try:
                serializer.save()
                return Response({'message' : 'Successfully joined in communty'}, status=status.HTTP_200_OK)
            except ValueError as e:
                print('exeption ====', str(e))
                return Response({'error' : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class ChatHistoryAPIView(generics.ListAPIView):
    serializer_class = MessageSerializer
    pagination_class = CustomMessagePagination

    def get_queryset(self):
        slug = self.kwargs['slug']
        community = Community.objects.get(slug=slug)
        print(slug, community)
        print(Message.objects.filter(community=community).order_by('-created_at'))
        return Message.objects.filter(community=community).order_by('created_at')



@api_view(['POST'])
def exit_community(request, slug):
    community = get_object_or_404(Community,slug=slug)

    if request.user not in community.participants.all():
        return Response({'error' : 'Your are not a member of this community'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        community.exit_participant(request.user)
        return Response({'message' : 'Successfully exited from community'}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'error' : str(e)}, status=status.HTTP_400_BAD_REQUEST)




class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return self.queryset.filter(recipient=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'}, status=status.HTTP_200_OK)