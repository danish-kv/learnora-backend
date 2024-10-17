from google.auth.transport import requests
from google.oauth2 import id_token
from .models import CustomUser
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from .api.user_serializers import CustomTokenObtainPairSerializer


class Google:
    """
    This class handles validation of Google OAuth2 tokens.
    """

    @staticmethod
    def validate(access_token):
        """
        Validate the Google OAuth2 access token.

        Args:
            access_token (str): The token received from Google.

        Returns:
            dict: Decoded token information if valid.
            str: Error message if the token is invalid or expired.
        """
        try:
            id_info = id_token.verify_oauth2_token(
                access_token, requests.Request(), settings.GOOGLE_CLIENT_ID
            )
            if 'accounts.google.com' in id_info['iss']:
                return id_info
        except Exception as e:
            return "Token is invalid or has expired."


def login_social_user(email, password, role):
    """
    Authenticate a user with their email and password and return JWT tokens.

    Args:
        email (str): The user's email.
        password (str): The user's password.
        role (str): The user's role.

    Returns:
        dict: User data including access and refresh tokens if authentication is successful.
    
    Raises:
        AuthenticationFailed: If the credentials are invalid or token generation fails.
    """
    user = authenticate(email=email, password=password)
    if not user:
        raise AuthenticationFailed('Invalid credentials.')

    token_serializer = CustomTokenObtainPairSerializer(
        data={'email': email, 'password': password, 'role': role}
    )

    # Validate the token serializer
    if token_serializer.is_valid():
        try:
            token_data = token_serializer.validated_data
            return {
                'id': user.id,
                'user': user.username,
                'email': user.email,
                'role': user.role,
                'access_token': token_data['access_token'],
                'refresh_token': token_data['refresh_token']
            }
        except KeyError as e:
            raise AuthenticationFailed(detail=f'Missing key: {str(e)}')
    else:
        raise AuthenticationFailed('Token generation failed.')


def register_social_user(provider, email, username, first_name, last_name, role):
    """
    Register or login a social user based on their provider and email.

    Args:
        provider (str): The social authentication provider (e.g., 'google').
        email (str): The user's email.
        username (str): The user's username.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        role (str): The user's role.

    Returns:
        dict: User data including access and refresh tokens.

    Raises:
        AuthenticationFailed: If there are issues during registration or login.
    """
    try:
        user = CustomUser.objects.get(email=email)

        # If user exists and provider matches, log them in
        if provider == user.auth_provider:
            result = login_social_user(email, settings.SOCIAL_AUTH_PASSWORD, role)
            return result
        else:
            raise AuthenticationFailed(
                detail=f'Please continue your login with {user.auth_provider}.'
            )

    except CustomUser.DoesNotExist:
        # If user does not exist, register a new social user
        new_user = CustomUser(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=settings.SOCIAL_AUTH_PASSWORD,
            auth_provider=provider,
            is_verified=True,
            role=role,
        )
        new_user.set_password(settings.SOCIAL_AUTH_PASSWORD)
        new_user.save()

        # Log in the newly registered user
        result = login_social_user(
            email=new_user.email, password=settings.SOCIAL_AUTH_PASSWORD, role=role
        )
        return result
