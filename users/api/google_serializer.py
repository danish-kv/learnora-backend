from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from ..models import CustomUser
from ..utils import Google, register_social_user


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