from django.shortcuts import render
from .models import Category, Course, Module, Comment, StudentCourseProgress, Review, Transaction, Note
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .serializers import CourseSerializer, CategorySerializer
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.files.uploadedfile import UploadedFile
import json
# Create your views here.



class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer




class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    lookup_field = 'slug'

    def create(self, request, *args, **kwargs):
        modules_data = json.loads(request.data.get('modules', '[]'))
        
        print('before loop in view')
        data = {}
        for key, value in request.data.items():
            print(key,value)
            if not isinstance(value, UploadedFile):
                data[key] = value
        
        print('module data ==',modules_data)
        for i, module in enumerate(modules_data):
            print('enum module ===', module)
            if f'video_{i}' in request.FILES:
                module['video'] = request.FILES[f'video_{i}']
            if f'notes_{i}' in request.FILES:
                module['notes'] = request.FILES[f'notes_{i}']
        
        data['modules'] = modules_data
        
        if 'thumbnail' in request.FILES:
            data['thumbnail'] = request.FILES['thumbnail']
        
        print('last data ===', request.data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(tutor=self.request.user)