from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .api.serializers import UserSerializers, CustomTokenObtainPairSerializer, GoogleSignInSerializer, UserProfileSerializers
from .signal import generate_otp, send_otp_email
from rest_framework_simplejwt.views import TokenObtainPairView
from .utils import register_social_user


 

# class ProfileImageView(APIView):
#     def patch(self, request):
#         data = request.data
#         print('requested ',data)
#         s = UserProfileSerializers(data=data)

#         if s.is_valid():
#             return Response(s.data, status=status.HTTP_201_CREATED)
#         return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)




class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        print('requested data === > ', data)
        
        user_serializer = UserSerializers(data=data)

        if user_serializer.is_valid():
            try:
                user = user_serializer.save()
                return Response(user_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                print('Exception:', e)
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print('Errors:', user_serializer.errors)
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class OTPVerification(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        print('otp  : ',email,otp)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data='User not found')
        
        if not user.otp:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='OTP is Expired')

        if user.otp == otp:
            user.otp = None
            user.is_verified = True
            user.save()
            print('Entered OTP is Correct')
            return Response(data='OTP verifed successfully', status=status.HTTP_200_OK)
        else:
            print('Entered OTP is Incorrect')
            return Response(data='Invalid OTP', status=status.HTTP_400_BAD_REQUEST)
        
     

class ResendOtpView(APIView):
    def post(self,request):
        email = request.data.get('email')
        print(email)

        if not email:
            return Response(data='Email is required', status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(data="User not Found", status=status.HTTP_404_NOT_FOUND)
        
        otp = generate_otp()
        user.otp = otp
        user.save()

        send_otp_email(email,otp)
        
        return Response(data='OTP resended successfully', status=status.HTTP_200_OK)

    

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class ForgetPassword(APIView):
    def post(self,request):
        print(request.data)
        try:
            email = request.data.get('email', None)
            password = request.data.get('password', None)

            if not email:
                return Response(data={'error' : 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response(data={'error' : 'User account not found'}, status=status.HTTP_404_NOT_FOUND)
            
            
            if password:
                user.set_password(password)
                user.save()
                print('Password changed successfully')
                return Response(data={'message': 'Password changed successfully'}, status=status.HTTP_201_CREATED)
            
            otp = generate_otp()
            user.otp = otp
            user.save()
            send_otp_email(email,otp)
            print('OTP sended in forget password')
            print(user.role)
            return Response(data={'message': 'OTP sent for password reset', 'role' : user.role }, status=status.HTTP_200_OK)
        
        except Exception as e:  
            return Response(data={'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Logout(APIView):
    def post(self,request):
        print('user logout', request.data)
        try:
            refresh = request.data['refresh']
            token = RefreshToken(refresh)
            token.blacklist()
            print('user logouted ')
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print('user logout not done')
            return Response(status=status.HTTP_400_BAD_REQUEST)
        




class GoogleSignInView(generics.GenericAPIView):
    serializer_class = GoogleSignInSerializer

    def post(self, request):
        print('data ====> ',request.data)
        serializer=self.serializer_class(data=request.data)
        print("serializer =====",serializer)
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
        
        print('User result:', result)
        
        return Response(result, status=status.HTTP_200_OK)
    
