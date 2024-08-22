from django.shortcuts import render
from .models import Category, Course, Module, Comment, StudentCourseProgress, Review, Transaction, Note
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status, generics
from .serializers import CourseSerializer, CategorySerializer, ModuleSerializer
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

    def get_queryset(self):
        if self.request.user.is_staff:
            return Course.objects.exclude(status='Pending')
        else: 
            return Course.objects.all()
        
    def perform_create(self, serializer):
        serializer.save(tutor=self.request.user.tutor_profile)   


class ModuleView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        modules_data = json.loads(request.data.get('modules'))
        print(modules_data)
        course_id = request.data.get('course')
        print(course_id)
        course = Course.objects.get(id=course_id)

        print(course)


        for i, data in enumerate(modules_data):
            print(i, data)
            title = data['title']
            description = data['description']
            duration = data['duration']
            video = request.FILES.get(f'video_{i}')
            notes = request.FILES.get(f'notes_{i}')

            Module.objects.create(
                course=course,
                description=description,
                duration = duration,
                title=title,
                video=video,
                notes=notes
            )

        return Response(data={'message' : 'Modules create sucessfully'}, status=status.HTTP_201_CREATED)



class ModuleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer


