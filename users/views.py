from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .api.user_serializers import (
    UserSerializers, 
    CustomTokenObtainPairSerializer, 
    UserStatusSerializer, 
    ChangePasswordSerializer
)
from .api.google_serializer import GoogleSignInSerializer
from .signal import generate_otp, send_otp_email
from .utils import register_social_user
from base.custom_permissions import IsAdmin, IsStudent
from rest_framework_simplejwt.views import TokenObtainPairView
from course.models import StudentCourseProgress, Course, Category
from course.serializers import CategorySerializer
from user_profile.serializers import TutorSerializer
from user_profile.models import Tutor
from django.db.models import Count, Avg, Sum


class RegisterView(APIView):
    """
    Handles user registration.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        
        user_serializer = UserSerializers(data=data)

        # Validate and save user data
        if user_serializer.is_valid():
            try:
                user_serializer.save()
                return Response(user_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerification(APIView):
    """
    Handles OTP verification for user registration or password reset.
    """
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        # Check if the user exists
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data='User not found')
        
        # Check OTP expiration and validity
        if not user.otp:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='OTP is Expired')

        if user.otp == otp:
            user.otp = None
            user.is_verified = True
            user.save()
            return Response(data='OTP verifed successfully', status=status.HTTP_200_OK)
        return Response(data='Invalid OTP', status=status.HTTP_400_BAD_REQUEST)
        

class ResendOtpView(APIView):
    """
    Resends OTP for verification.
    """
    def post(self,request):
        email = request.data.get('email')

        if not email:
            return Response(data='Email is required', status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(data="User not Found", status=status.HTTP_404_NOT_FOUND)
        
       # Generate and send new OTP
        otp = generate_otp()
        user.otp = otp
        user.save()
        send_otp_email(email, otp)

        return Response(data='OTP resent successfully', status=status.HTTP_200_OK)

    
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom Token Obtain Pair View using a custom serializer.
    """
    serializer_class = CustomTokenObtainPairSerializer


class ForgetPassword(APIView):
    """
    Handles the password reset process including OTP generation.
    """
    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        if not email:
            return Response(data={'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(data={'error': 'User account not found'}, status=status.HTTP_404_NOT_FOUND)

        # If password is provided, change it directly
        if password:
            user.set_password(password)
            user.save()
            return Response(data={'message': 'Password changed successfully'}, status=status.HTTP_201_CREATED)

        # If password is not provided, generate OTP for password reset
        otp = generate_otp()
        user.otp = otp
        user.save()
        send_otp_email(email, otp)

        return Response(data={'message': 'OTP sent for password reset', 'role': user.role}, status=status.HTTP_200_OK)
       

class Logout(APIView):
    """
    Handles user logout and token blacklist.
    """
    def post(self, request):
        try:
            refresh = request.data['refresh']
            token = RefreshToken(refresh)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GoogleSignInView(generics.GenericAPIView):
    """
    Handles Google Sign-In using a custom serializer.
    """
    serializer_class = GoogleSignInSerializer

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_data=serializer.validated_data
        result = register_social_user(
            provider=user_data['provider'],
            email=user_data['email'],
            username=user_data['username'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role']
        )
        
        return Response(result, status=status.HTTP_200_OK)
    


class UserStatusUpdate(generics.UpdateAPIView):
    """
    Updates user status, allowed only for admins.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserStatusSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'pk'


class StudentProfileViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing student profile.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializers
    permission_classes = [IsStudent]  

    def get_queryset(self):
        user = self.request.user
        return CustomUser.objects.filter(id=user.id)    


class ChangePassword(APIView):
    """
    Handles changing user password.
    """
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Password updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LandingPage(viewsets.ViewSet):
    """
    Retrieves the landing page statistics and data.
    """
    def list(self, request):
        try:
            total_course_completion = StudentCourseProgress.objects.filter(progress='Completed').count()
            total_tutor = Tutor.objects.count()
            total_student = CustomUser.objects.filter(role='student').count()
            total_course = Course.objects.count()

            # Retrieve top categories with course stats
            categories = (
                Category.objects.filter(is_active=True, status='Approved')
                .annotate(
                    total_courses=Count('courses', distinct=True),  
                    total_enrollment=Sum('courses__total_enrollment'),  
                    average_rating=Avg('courses__reviews__rating') 
                )
                .order_by('-id')[:6]
            )

            category_serializer = CategorySerializer(categories, many=True)

            # Retrieve verified tutors
            tutors = Tutor.objects.filter(status = 'Verified', user__is_verified=True, user__is_active=True)
            tutor_data = TutorSerializer(tutors, many=True)

            # Retrieve student profile if not null
            students = CustomUser.objects.filter(role='student').exclude(profile__isnull=True).exclude(profile__exact='')
            students_data = UserSerializers(students, many=True)

            # Prepare response data
            data = {
                'total_course_completion': total_course_completion,
                'total_tutor': total_tutor,
                'total_student': total_student,
                'total_course': total_course,
                "categories": category_serializer.data,
                'tutors' : tutor_data.data,
                'students' : students_data.data 
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
