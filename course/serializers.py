from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Category, Course, Module, StudentCourseProgress, Review, Transaction, Note
from users.models import CustomUser
from user_profile.serializers import TutorSerializer
from users.api.user_serializers import UserSerializers



class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def validate_name(self,value):
        if not value.strip():
            print('yes')
            raise serializers.ValidationError('Category name cannot be empty')
        
        if Category.objects.filter(name=value).exists():
            raise serializers.ValidationError('Category already exists')
        
        return value



class ModuleSerializer(ModelSerializer):
    student_notes = serializers.SerializerMethodField()
    is_watched = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()


    class Meta:
        model = Module
        fields = "__all__"

    def validate_video(self, value):

        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError('Video file size should not exceed 50 MB')
        
        if not value.name.endswith(('mp4', 'mov', 'avi')):
            raise serializers.ValidationError('Invalid video type')
        
        return value
    

    def validate_notes(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('Notes file size should not be exceed 10MB')
        
        if not value.name.endswith(('pdf', 'docx')):
            raise serializers.ValidationError('Invalid file type for notes')
        return value
    
    def get_student_notes(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            notes = Note.objects.filter(module=obj, user=request.user)
            return [{"id": note.id, "content": note.content , 'timeline' : note.timeline} for note in notes]
        return None

    def get_is_watched(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            progress = StudentCourseProgress.objects.filter(student=request.user, course=obj.course).first()
            return obj in progress.watched_modules.all() if progress else False
        return False

    def get_is_liked(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            progress = StudentCourseProgress.objects.filter(student=request.user, course=obj.course).first()
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



class CourseSimpleSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'rental_price']  


class ReviewSerializer(ModelSerializer):
    user = UserSerializers(read_only = True)
    course = CourseSimpleSerializer(read_only=True)
    is_my_review = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = '__all__'

    def get_is_my_review(self, obj):
        user = self.context['request'].user
        return obj.user == user
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
 



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

    def validate_thumbnail(self, value):

        max_file_size = 2 * 1024 * 1024 
        allowed_formats = ['image/jpeg', 'image/png']

        if value.size > max_file_size:
            raise serializers.ValidationError('Thumbnail size should not be exceed 2MB')
        
        if value.content_type not in allowed_formats:
            raise serializers.ValidationError("Thumbnail image format should be JPEG or PNG.")

        return value
    
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



class NotesSerializer(ModelSerializer):
    module = serializers.SerializerMethodField()  

    class Meta:
        model = Note
        fields = "__all__"

    def get_module(self, obj):
        return ModuleSerializer(obj.module, context=self.context).data
    






class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializers(read_only=True)
    course = CourseSimpleSerializer(read_only=True)
    class Meta:
        model = Transaction
        fields = '__all__'



class StudentCourseProgressSerializer(ModelSerializer):
    course = CourseSerializer(read_only=True)  
    student = UserSerializers(read_only=True)
    
    class Meta:
        model = StudentCourseProgress
        fields = '__all__'

