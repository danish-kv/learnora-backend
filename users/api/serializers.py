from rest_framework import serializers
from ..models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework.exceptions import PermissionDenied




class UserProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['profile']

    def validate(self, attrs):
        print('check',attrs)
        return attrs





class UserSerializers(serializers.ModelSerializer):
    

    class Meta:
        model = CustomUser
        fields = [ 'username', 'first_name', 'last_name', 'email', 'password', 'bio', 'phone', 'dob', 'date_joined', 'role' ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        print('Validating data ===', validated_data)

        if CustomUser.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists'})

        password = validated_data.pop('password', None)
        role = validated_data.pop('role', None)        
        
        user = CustomUser.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
        if role:
            user.role = role
        user.save()

        print('role', role)
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

    @classmethod
    def get_token(cls, user: CustomUser):
        token = super().get_token(user)
        print(f"Validating user: {user}")
        print(f"User role: {user.role}")

        if user.is_superuser:
            print('is a admin')
            token['is_admin'] = True
            token['role'] = 'admin'
        elif user.role == 'tutor':
            token['is_tutor'] = True
            print('is a Tutor')
        else:        
            print('is a studnet')
            token['user'] = user.username
            token['email'] = user.email
            token['is_active'] = user.is_active  
            token['role'] = user.role


        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        print(f"User in validate: {self.user}")

        data.update({'access_token': data.pop('access')})
        data.update({'refresh_token': data.pop('refresh')})
        data.update({'role': self.user.role})
        data.update({'user': self.user.username})
        # data.update({'': self.user.is_active})

        return data



















from ..utils import Google, register_social_user
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


class GoogleSignInSerializer(serializers.Serializer):
    access_token = serializers.CharField(min_length=6)
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    def validate(self, attrs):
        access_token = attrs.get('access_token')
        role = attrs.get('role')

        print('Validating access token...')
        google_user_data = Google.validate(access_token)
        print('Google user data:', google_user_data)

        if not google_user_data:
            raise serializers.ValidationError("This token is invalid or has expired")
        
        try:
            userId=google_user_data['sub']
            
        except Exception as e:
            print(e, 'token is invalid or has expired')
            raise serializers.ValidationError("this token is invalid or has expired")
        
        if google_user_data['aud'] != settings.GOOGLE_CLIENT_ID:
            print('worrrrrrrrrr')
            raise AuthenticationFailed(detail='could not verify user')
        

        
        email = google_user_data.get('email', '')
        first_name = google_user_data.get('given_name', '')
        last_name = google_user_data.get('family_name', '')
        username = google_user_data.get('name', '')
        provider='google'      

        return {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'provider': provider,
            'role': role
        }