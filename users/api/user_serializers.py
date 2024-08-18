from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, ValidationError
from ..models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework.exceptions import PermissionDenied
from user_profile.models import Tutor
from ..signal import generate_otp, send_otp_email
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now






class UserSerializers(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [ 'id', 'username', 'first_name', 'last_name', 'last_login', 'email', 'password', 'bio',
                   'phone', 'dob', 'date_joined', 'role', 'profile', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        print('Validating data ===', validated_data)

        if CustomUser.objects.filter(email=validated_data['email']).exists():
            raise ValidationError({'email': 'A user with this email already exists'})

        password = validated_data.pop('password', None)  
        
        user = CustomUser.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
        user.save()

        print('role', user.role)
        print('pass', password)



 
        return user

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if key == "password":
                instance.set_password(value)
            else:
                setattr(instance, key, value)
        instance.save()
        return instance
        



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    role = serializers.CharField(write_only=True)

    @classmethod
    def get_token(cls, user: CustomUser):
        token = super().get_token(user)
        print(f"Validating user: {user}")
        print(f"User role: {user.role}")
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
            print('is a Tutor')
        else:        
            print('is a studnet')
            token['user'] = user.username
            token['is_active'] = user.is_active 
            token['email'] = user.email
            token['is_verified'] = user.is_verified 
            token['role'] = user.role


        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        print(f"User in validate: {self.user}")

        user = self.user
        print(user)

        requested_role = attrs.get('role')
        if user.role != requested_role:
            raise serializers.ValidationError({
                'error' : 'Your are not authrized person'
            })
        if not user.is_verified:
            print(user.is_verified)
            print('user is not verified')
            otp = generate_otp()
            user.otp = otp
            user.save()
            print(otp, user.email)
            send_otp_email(user.email, otp)

            

        data.update({'access_token': data.pop('access')})
        data.update({'refresh_token': data.pop('refresh')})
        data.update({'role': user.role})
        data.update({'user': user.username})


        return data


class UserStatusSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['is_active']