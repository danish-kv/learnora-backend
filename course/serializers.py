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



class CustomTutorSerializer(ModelSerializer):
    class Meta:
        model  = CustomUser
        fields = ['id', 'username' ]


class ModuleSerializer(ModelSerializer):
    # video = serializers.FileField(required=False, allow_null=True)
    # notes = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Module
        fields = ['title', 'description', 'video', 'notes']


class CourseSerializer(ModelSerializer):
    tutor = TutorSerializer(read_only=True)
    modules = ModuleSerializer(many=True, required=False)
    # thumbnail = serializers.ImageField(required=False)

    class Meta:
        model = Course
        fields = '__all__'

    def create(self, validated_data):
        print('validating data = =======', validated_data)
        modules_data = validated_data.pop('modules', [])
        print('poped module data ==== ',modules_data)
        user = validated_data.pop('tutor', None)
        tutor_id = Tutor.objects.get(user=user)
        
        course = Course.objects.create(tutor=tutor_id, **validated_data)
        
        for module_data in modules_data:
            print('data in loop',module_data)
            video = module_data.pop('video', None)
            notes = module_data.pop('notes', None)
            module = Module.objects.create(course=course, **module_data)

            print('video ===== ',video, video.name)
            print('notes ====',notes, notes.name)
            if video:
                module.video.save(video.name, video, save=True)
            if notes:
                module.notes.save(notes.name, notes, save=True)
        
        return course

