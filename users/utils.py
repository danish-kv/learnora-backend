from google.auth.transport import requests
from google.oauth2 import id_token 
from .models import CustomUser
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from .api.user_serializers import CustomTokenObtainPairSerializer


class Google():
    @staticmethod
    def validate(access_token):
        try:
            id_info=id_token.verify_oauth2_token(access_token, requests.Request(), settings.GOOGLE_CLIENT_ID)
            if 'accounts.google.com' in id_info['iss']:
                return id_info
            
        except Exception as e:
            return "token is invalid or has expired"


def login_social_user(email, password, role):
    user=authenticate(email=email, password=password)
    if not user:
        raise AuthenticationFailed('Invalid credentials.')

    token_serializer = CustomTokenObtainPairSerializer(data={'email': email, 'password': password, 'role' : role})

    token_data = token_serializer.get_token(user)

    if token_serializer.is_valid():
        token_data = token_serializer.validated_data
        try:
            return {
            'user' : user.username,
            'email' : user.email,
            'role' : user.role,
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token']
            }

        except KeyError as e:
            raise AuthenticationFailed(detail=f'Missing key: {str(e)}')
    else:
        raise AuthenticationFailed('Token generation failed.')

    

def register_social_user(provider, email,username, first_name, last_name, role):

    try:
        user=CustomUser.objects.get(email=email)
        
        if provider == user.auth_provider:
            result = login_social_user(email,settings.SOCIAL_AUTH_PASSWORD, role)   
            return result
        else: raise AuthenticationFailed(
            detail = f'please continue your login with {user.auth_provider}'
        )
        
    except CustomUser.DoesNotExist:
            new_user = CustomUser(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=settings.SOCIAL_AUTH_PASSWORD,
                auth_provider=provider,
                email_verified=True,
                role=role,
            )
            new_user.set_password(settings.SOCIAL_AUTH_PASSWORD)
            new_user.save()

            result = login_social_user(email=new_user.email, password=settings.SOCIAL_AUTH_PASSWORD, role = role)
            return result
        



