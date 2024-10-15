from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import (
    Category,
    Course,
    Module,
    StudentCourseProgress,
    Review,
    Transaction,
    Note,
)
from user_profile.serializers import TutorSerializer
from users.api.user_serializers import UserSerializers

from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model. Provides read-only fields for 
    total courses, total enrollment, and average rating.
    """
    total_courses = serializers.IntegerField(read_only=True, required=False) 
    total_enrollment = serializers.IntegerField(read_only=True, required=False) 
    average_rating = serializers.FloatField(read_only=True, required=False) 

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'is_active', 'status', 'total_courses', 'total_enrollment', 'average_rating']

    def validate_name(self, value):
        """
        Validates the category name to ensure it is not empty 
        and does not already exist.
        """
        if not value.strip():
            raise serializers.ValidationError('Category name cannot be empty')

        if Category.objects.filter(name=value).exists():
            raise serializers.ValidationError('Category already exists')

        return value


class ModuleSerializer(ModelSerializer):
    """
    Serializer for the Module model. Includes methods to check
    student notes, watch status, and like status, along with
    validation for video and notes files.
    """
    student_notes = serializers.SerializerMethodField()
    is_watched = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = "__all__"

    def validate_video(self, value):
        """
        Validates the uploaded video file to ensure it is not 
        larger than 50 MB and has a valid format.
        """
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError('Video file size should not exceed 50 MB')
        
        if not value.name.endswith(('mp4', 'mov', 'avi')):
            raise serializers.ValidationError('Invalid video type')
        
        return value
    

    def validate_notes(self, value):
        """
        Validates the uploaded notes file to ensure it is not 
        larger than 10 MB and has a valid format.
        """
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('Notes file size should not be exceed 10MB')
        
        if not value.name.endswith(('pdf', 'docx')):
            raise serializers.ValidationError('Invalid file type for notes')
        return value
    
    def get_student_notes(self, obj):
        """
        Retrieves the notes associated with the student for the module.
        """
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            notes = Note.objects.filter(module=obj, user=request.user)
            return [{"id": note.id, "content": note.content, 'timeline': note.timeline} for note in notes]
        return None

    def get_is_watched(self, obj):
        """
        Checks if the module has been watched by the authenticated student.
        """
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            progress = StudentCourseProgress.objects.filter(student=request.user, course=obj.course).first()
            return obj in progress.watched_modules.all() if progress else False
        return False

    def get_is_liked(self, obj):
        """
        Checks if the module has been liked by the authenticated student.
        """
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            progress = StudentCourseProgress.objects.filter(student=request.user, course=obj.course).first()
            return obj in progress.liked_modules.all() if progress else False

    def update(self, instance, validated_data):
        """
        Updates the module instance with validated data. 
        Deletes old video and notes files if new ones are provided.
        """
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
    """
    Simple serializer for the Course model to expose 
    minimal information.
    """
    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'rental_price']


class ReviewSerializer(ModelSerializer):
    """
    Serializer for the Review model. Includes user information 
    and the course data related to the review.
    """
    user = UserSerializers(read_only=True)
    course_data = serializers.SerializerMethodField()  
    is_my_review = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'

    def get_is_my_review(self, obj):
        """
        Checks if the authenticated user is the one who wrote the review.
        """
        request = self.context.get('request', None)  
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.user == request.user
        return False 

    def create(self, validated_data):
        """
        Associates the authenticated user with the review upon creation.
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def get_course_data(self, obj):
        """
        Retrieves the course data associated with the review.
        """
        course = obj.course 
        return CourseSimpleSerializer(course).data if course else None


class CourseSerializer(ModelSerializer):
    """
    Serializer for the Course model. Includes detailed information 
    such as modules, reviews, and progress.
    """
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    tutor = TutorSerializer(read_only=True)
    modules = serializers.SerializerMethodField()  
    reviews = ReviewSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)
    category_data = CategorySerializer(source='category', read_only=True)
    requested_course_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'

    def get_modules(self, obj):
        """
        Retrieves the modules with the context passed to include the request.
        """
        modules = Module.objects.filter(course=obj)
        return ModuleSerializer(modules, many=True, context=self.context).data

    def validate_thumbnail(self, value):
        """
        Validates the uploaded thumbnail image to ensure it is not 
        larger than 2 MB and has a valid format.
        """
        max_file_size = 2 * 1024 * 1024 
        allowed_formats = ['image/jpeg', 'image/png']

        if value.size > max_file_size:
            raise serializers.ValidationError('Thumbnail size should not exceed 2MB')
        
        if value.content_type not in allowed_formats:
            raise serializers.ValidationError("Thumbnail image format should be JPEG or PNG.")

        return value

    def get_progress(self, obj):
        """
        Retrieves the progress of the authenticated student for the course.
        """
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            progress = StudentCourseProgress.objects.filter(student=request.user, course=obj).first()
            if progress:
                return StudentCourseProgressSerializer(progress).data
        return None
        
    def get_average_rating(self, obj):
        """
        Returns the average rating of the course.
        """
        return obj.average_rating
    
    def get_requested_course_count(self, obj):
        """
        Counts the number of requested courses.
        """
        return Course.objects.filter(status='Requested').count()

    def update(self, instance, validated_data):
        """
        Updates the course instance with validated data.
        Deletes old thumbnail image if a new one is provided.
        """
        new_photo = validated_data.get('thumbnail', None)
        if new_photo and instance.thumbnail:
            instance.thumbnail.delete(save=True)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class NotesSerializer(ModelSerializer):
    """
    Serializer for the Note model. Includes module data.
    """
    module = ModuleSerializer(read_only=True)  # for full module data for output
    module_id = serializers.PrimaryKeyRelatedField(
        queryset=Module.objects.all(), write_only=True, source='module'
    )  # Accept module ID for input

    class Meta:
        model = Note
        fields = "__all__"



class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transaction model. Provides information 
    about the user and associated course.
    """
    user = UserSerializers(read_only=True)
    course = CourseSimpleSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'


class StudentCourseProgressSerializer(ModelSerializer):
    """
    Serializer for the StudentCourseProgress model. Includes course 
    and student information.
    """
    course = CourseSerializer(read_only=True)  
    student = UserSerializers(read_only=True)
    
    class Meta:
        model = StudentCourseProgress
        fields = '__all__'
