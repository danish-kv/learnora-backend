from rest_framework.serializers import ModelSerializer, JSONField, FileField
from rest_framework import serializers
from .models import Category, Course, Module, Comment, StudentCourseProgress, Review, Transaction, Note
from users.models import CustomUser
from user_profile.serializers import TutorSerializer
from user_profile.models import Tutor



class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ModuleSerializer(ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"

class CourseSerializer(ModelSerializer):
    tutor = TutorSerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = '__all__'