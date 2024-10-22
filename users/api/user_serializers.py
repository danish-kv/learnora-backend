from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, ValidationError
from django.contrib.auth import authenticate
from ..models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from ..signal import generate_otp, send_otp_email
from django.utils.timezone import now
from course.models import Course

# Serializer for enrolled courses
class EnrolledCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'  # Serialize all fields of the Course model


# Serializer for the CustomUser model
class UserSerializers(ModelSerializer):
    enrolled_courses = serializers.SerializerMethodField(read_only=True)  # Add a field to get enrolled courses

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name', 'last_login', 'email',
            'password', 'bio', 'phone', 'dob', 'date_joined', 'role', 'profile',
            'is_active', 'enrolled_courses'
        ]
        extra_kwargs = {'password': {'write_only': True}}  # Password should only be writable

    def create(self, validated_data):
        """Create a new user instance with the validated data."""
        if CustomUser.objects.filter(email=validated_data['email']).exists():
            raise ValidationError({'email': 'A user with this email already exists'})

        password = validated_data.pop('password', None)  # Extract password from validated data
        user = CustomUser.objects.create_user(**validated_data)  # Create user instance

        if password:
            user.set_password(password)  # Set the user's password
        user.save()  # Save the user to the database

        return user

    def update(self, instance, validated_data):
        """Update an existing user instance with the validated data."""
        for key, value in validated_data.items():
            if key == "password":
                instance.set_password(value)  # Set password if provided
            else:
                setattr(instance, key, value)  # Update other fields
        instance.save()  # Save changes
        return instance

    def get_enrolled_courses(self, obj):
        """Get the courses in which the user is enrolled."""
        enroll_course = Course.objects.filter(student_progress__student=obj)  # Get enrolled courses
        return EnrolledCourseSerializer(enroll_course, many=True).data  # Serialize and return courses


# Custom token serializer for JWT authentication
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(write_only=True)  # Email for authentication
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})  # Password input
    role = serializers.CharField(write_only=True)  # User role for validation

    @classmethod
    def get_token(cls, user: CustomUser):
        """Create and return a token for the given user."""
        token = super().get_token(user)  # Generate a token
        user.last_login = now()  # Update last login time
        user.save()  # Save user data

        # Add additional claims based on user role
        if user.is_superuser:
            token['is_admin'] = True
            token['role'] = 'admin'
        elif user.role == 'tutor':
            token['is_tutor'] = True
            token['id'] = user.id
            token['is_verified'] = user.is_verified
            token['is_active'] = user.is_active 
            token['status'] = user.tutor_profile.status
        else:        
            token['user'] = user.username
            token['id'] = user.id
            token['profile'] = user.profile
            token['is_active'] = user.is_active 
            token['email'] = user.email
            token['is_verified'] = user.is_verified 
            token['role'] = user.role

        return token

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        requested_role = attrs.get('role')

        # First, check if the user exists
        try:
            user = CustomUser.objects.get(email=email)
            print(user)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({
                'error': 'No account found with the given email.'
            }, code='no_account')

        # Now check if the user is active
        if not user.is_active:
            raise serializers.ValidationError({
                'error': 'Your account has been blocked by the admin.'
            }, code='blocked')

        # Authenticate the user
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError({
                'error': 'Invalid credentials'
            }, code='authentication')

        # Check role
        if user.role != requested_role:
            raise serializers.ValidationError({
                'error': 'You are not authorized for this role'
            }, code='authorization')

        # Check if verified
        if not user.is_verified:
            otp = generate_otp()
            user.otp = otp
            user.save()
            send_otp_email(user.email, otp)
            raise serializers.ValidationError({
                'error': 'Account not verified. An OTP has been sent to your email.',
                'require_verification': True
            }, code='unverified')

        # If the user is valid, active, and authenticated
        self.user = user
        data = super().validate(attrs)

        data.update({
            'access_token': data.pop('access'),
            'refresh_token': data.pop('refresh'),
            'role': user.role,
            'user': user.username
        })

        return data



# Serializer for updating user status
class UserStatusSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['is_active']  # Only the active status field


# Serializer for changing user passwords
class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)  # Old password required
    new_password = serializers.CharField(required=True)  # New password required
    confirm_password = serializers.CharField(required=True)  # Password confirmation required

    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password', 'confirm_password']

    def validate(self, attrs):
        """Validate the old password and confirm the new password."""
        user = self.context['request'].user

        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'Old password is incorrect'})
        
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': "New Password does not match"})
        
        return attrs    

    def save(self, **kwargs):
        """Save the new password for the user."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])  # Set new password
        user.save()  # Save changes
