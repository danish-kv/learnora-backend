from django.shortcuts import render
from .serializer import CommunitySerializer, MessageSerializer, CreateCommunitySerializer
from .models import Community, Message
from rest_framework import status, generics
from rest_framework.response import Response
from base.custom_permissions import IsTutor, IsStudent
from rest_framework import viewsets
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




