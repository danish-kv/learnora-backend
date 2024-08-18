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
            print('infoffff goog', id_info)
            if 'accounts.google.com' in id_info['iss']:
                return id_info
            
        except Exception as e:
            print('Validation error:', e)
            return "token is invalid or has expired"


def login_social_user(email, password, role):
    print(email, password, role)
    user=authenticate(email=email, password=password)
    print(user,'already data found')
    if not user:
        raise AuthenticationFailed('Invalid credentials.')

    token_serializer = CustomTokenObtainPairSerializer(data={'email': email, 'password': password, 'role' : role})

    print('toke serializers',token_serializer)
    token_data = token_serializer.get_token(user)
    print('token data, ', token_data)

    if token_serializer.is_valid():
        token_data = token_serializer.validated_data
        print('Token data:', token_data)
        try:
            print('Returning token data')
            return {
            'user' : user.username,
            'email' : user.email,
            'role' : user.role,
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token']
            }

        except KeyError as e:
            print('KeyError:', e)
            raise AuthenticationFailed(detail=f'Missing key: {str(e)}')
    else:
        print('Token serializer is invalid', token_serializer.errors)
        raise AuthenticationFailed('Token generation failed.')

    

def register_social_user(provider, email,username, first_name, last_name, role):

    try:
        user=CustomUser.objects.get(email=email)
        
        if provider == user.auth_provider:
            print('1111111')
            result = login_social_user(email,settings.SOCIAL_AUTH_PASSWORD, role)   
            return result
        else: raise AuthenticationFailed(
            detail = f'please continue your login with {user.auth_provider}'
        )
        
    except CustomUser.DoesNotExist:
            print('222222222')
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
            print("user created in using Google",new_user)

            result = login_social_user(email=new_user.email, password=settings.SOCIAL_AUTH_PASSWORD, role = role)
            return result
        



