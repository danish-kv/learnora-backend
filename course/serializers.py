from rest_framework.serializers import ModelSerializer, JSONField, FileField
from rest_framework import serializers
from .models import Category, Course, Module, Comment, StudentCourseProgress, Review, Transaction, Note
from users.models import CustomUser
from user_profile.serializers import TutorSerializer
from user_profile.models import Tutor
from users.api.user_serializers import UserSerializers



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
    is_watched = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()


    class Meta:
        model = Module
        fields = "__all__"

    def get_student_notes(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            notes = Note.objects.filter(module=obj, user=user)
            return NotesSerializer(notes, many=True).data
        
    def get_is_watched(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            progress =  StudentCourseProgress.objects.filter(student=user, course=obj.course).first()
            return obj in progress.watched_modules.all() if progress else False
        return False
    
    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            progress = StudentCourseProgress.objects.filter(student=user, course=obj.course).first()
            return obj in progress.liked_modules.all() if progress else False
        
    
    def update(self, instance, validated_data):

        new_video = validated_data.get('video', None)
        if new_video and instance.video:
            instance.video.delete(save=False)

        new_notes = validated_data.get('notes', None)
        if new_notes and instance.notes:
            instance.notes.delete(save=False)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance




class StudentCourseProgressSerializer(ModelSerializer):
    class Meta:
        model=StudentCourseProgress
        fields = '__all__'

class ReviewSerializer(ModelSerializer):
    user = UserSerializers(read_only = True)
    is_my_review = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = '__all__'

    def get_is_my_review(self, obj):
        user = self.context['request'].user
        return obj.user == user
    
 



class CourseSerializer(ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    tutor = TutorSerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)
    category_data = CategorySerializer(source='category' ,read_only =True)
    requested_course_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Course
        fields = '__all__'

    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            progress = StudentCourseProgress.objects.filter(student=request.user, course=obj).first()
            if progress:
                return StudentCourseProgressSerializer(progress).data
        return None
        
    def get_average_rating(self,obj):
        return obj.average_rating
    
    def get_requested_course_count(self, obj):
        return Course.objects.filter(status='Requested').count()
        

    

    def update(self, instance, validated_data):

        new_photo = validated_data.get('thumbnail', None)
        if new_photo and instance.thumbnail:
            instance.thumbnail.delete(save=True)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance
