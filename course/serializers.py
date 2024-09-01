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


class NotesSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"


class ModuleSerializer(ModelSerializer):
    student_notes = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = "__all__"

    def get_student_notes(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            notes = Note.objects.filter(module=obj, user=user)
            return NotesSerializer(notes, many=True).data




class StudentCourseProgressSerializer(ModelSerializer):
    class Meta:
        model=StudentCourseProgress
        fields = '__all__'


class ReviewSerializer(ModelSerializer):
    is_my_review = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = '__all__'

    def get_is_my_review(self, obj):
        user = self.context['request'].user
        return obj.user == user
    
 



class CourseSerializer(ModelSerializer):
    category = CategorySerializer(read_only=True)
    tutor = TutorSerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Course
        fields = '__all__'

    def get_progress(self, obj):
        request = self.context['request']
        if request and request.user and request.user.is_authenticated:
            progress = StudentCourseProgress.objects.filter(student=request.user, course=obj).first()
            if progress:
                return StudentCourseProgressSerializer(progress).data
        return None
        
    def get_average_rating(self,obj):
        return obj.average_rating