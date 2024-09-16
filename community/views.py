from django.shortcuts import render
from .serializer import CommunitySerializer, MessageSerializer, CreateCommunitySerializer, JoinCommunitySerializer
from .models import Community, Message
from rest_framework import status, generics, views
from rest_framework.response import Response
from base.custom_permissions import IsTutor, IsStudent
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
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
    permission_classes = []


class JoinCommunityAPIView(APIView):
    # permission_classes = []

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

    def get_queryset(self):
        slug = self.kwargs['slug']
        community = Community.objects.get(slug=slug)
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
