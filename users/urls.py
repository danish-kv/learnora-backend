from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, OTPVerification, CustomTokenObtainPairView, ResendOtpView, 
    ForgetPassword, Logout, GoogleSignInView, UserStatusUpdate, 
    StudentProfileViewSet, ChangePassword, LandingPage
)

# Setting up the DefaultRouter for StudentProfile and LandingPage
router = DefaultRouter()
router.register(r'student-profile', StudentProfileViewSet, basename='student-profile')
router.register(r'landing-page', LandingPage, basename='landing-page')

urlpatterns = [
    path('', include(router.urls)),  # Includes the router URLs for the viewsets
    path('register/', RegisterView.as_view(), name='register'),  # Registration route
    path('otp-verify/', OTPVerification.as_view(), name='otp_verify'),  # OTP verification
    path('forget-password/', ForgetPassword.as_view(), name='forget_password'),  # Forgot password
    path('otp-resend/', ResendOtpView.as_view(), name='otp_resend'),  # Resend OTP
    path('login/token/', CustomTokenObtainPairView.as_view(), name='login_token_obtain_pair'),  # JWT login route
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Token refresh route for JWT
    path('logout/', Logout.as_view(), name='logout'),  # Logout route
    path('google/', GoogleSignInView.as_view(), name='google'),  # Google Sign-In route
    path('user/<int:pk>/status/', UserStatusUpdate.as_view(), name='change_status'),  # User status update by ID
    path('change-password/', ChangePassword.as_view(), name='change-password')  # Change password route
]
