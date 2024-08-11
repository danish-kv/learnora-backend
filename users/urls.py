from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, OTPVerification, CustomTokenObtainPairView, ResendOtpView, ForgetPassword, Logout, GoogleSignInView
from rest_framework_simplejwt.views import TokenRefreshView

# router = DefaultRouter()
# router.register(r'profile-image', ProfileImageView, basename='imag')


urlpatterns = [
    # path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('otp-verify/', OTPVerification.as_view(), name='otp_verify'),
    path('forget-password/', ForgetPassword.as_view(), name='forget-password'),
    path('otp-resend/', ResendOtpView.as_view(), name='otp_resend'),
    path('login/token/', CustomTokenObtainPairView.as_view(), name='login_token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', Logout.as_view(), name='logout'),
    path('google/', GoogleSignInView.as_view(), name='google'),
    # path('profile-image/', ProfileImageView.as_view(), name='profile-image'),
    # path('api/student-only/', StudentOnlyView.as_view(), name='student_only'),
    # path('api/tutor-only/', TutorrOnlyView.as_view(), name='ins_only'),
]