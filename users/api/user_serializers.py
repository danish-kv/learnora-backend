from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, ValidationError
from ..models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework.exceptions import PermissionDenied
from user_profile.models import Tutor
from ..signal import generate_otp, send_otp_email
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now
from course.models import Course





class EnrolledCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'




class UserSerializers(ModelSerializer):
    enrolled_courses = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CustomUser
        fields = [ 'id', 'username', 'first_name', 'last_name', 'last_login', 'email', 'password', 'bio',
                   'phone', 'dob', 'date_joined', 'role', 'profile', 'is_active', 'enrolled_courses']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):

        if CustomUser.objects.filter(email=validated_data['email']).exists():
            raise ValidationError({'email': 'A user with this email already exists'})

        password = validated_data.pop('password', None)  
        
        user = CustomUser.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        print('passsword', password)

        return user

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if key == "password":
                instance.set_password(value)
            else:
                setattr(instance, key, value)
        instance.save()
        return instance
    
    def get_enrolled_courses(self, obj):
        enroll_course = Course.objects.filter(student_progress__student=obj)
        return EnrolledCourseSerializer(enroll_course, many=True).data
        



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    role = serializers.CharField(write_only=True)

    @classmethod
    def get_token(cls, user: CustomUser):
        token = super().get_token(user)
        user.last_login = now()
        user.save()

        if user.is_superuser:
            print('is a admin')
            token['is_admin'] = True
            token['role'] = 'admin'
        elif user.role == 'tutor':
            token['is_tutor'] = True
            token['is_verified'] = user.is_verified
            token['is_active'] = user.is_active 
            token['status'] = user.tutor_profile.status
        else:        
            token['user'] = user.username
            token['is_active'] = user.is_active 
            token['email'] = user.email
            token['is_verified'] = user.is_verified 
            token['role'] = user.role


        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        requested_role = attrs.get('role')

        if user.role != requested_role:
            raise serializers.ValidationError({
                'error' : 'Your are not authrized person'
            }, code='authorization')
        
        if not user.is_verified:
            otp = generate_otp()
            user.otp = otp
            user.save()
            send_otp_email(user.email, otp)
        
        
        if not user.is_active:
            print('not acsfgdsdtive')
            raise serializers.ValidationError({
                'error': 'Your account has been blocked by the admin.'
            }, code='blocked')

        data.update({'access_token': data.pop('access')})
        data.update({'refresh_token': data.pop('refresh')})
        data.update({'role': user.role})
        data.update({'user': user.username})


        return data




class UserStatusSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['is_active']