from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from .models import Tutor, Skill, Education, Experience
from users.models import CustomUser
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import TutorSerializer

# Create your views here.




import json

class TutorProfile(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data.copy()  # Make a mutable copy of the data
        
        try:
            if 'education' in data:
                data['education'] = json.loads(data['education'][0] if isinstance(data['education'], list) else data['education'])
            if 'experiences' in data:
                data['experiences'] = json.loads(data['experiences'][0] if isinstance(data['experiences'], list) else data['experiences'])
            if 'skills' in data and isinstance(data['skills'], list) and len(data['skills']) == 1:
                data['skills'] = data['skills'][0].split(',')  # Assuming skills are comma-separated
        except json.JSONDecodeError as e:
            return Response({'error': f'Invalid JSON: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        print('tutor profile',data)

        if 'email' in data:
            print(data['email'])
            user = CustomUser.objects.get(email=data['email'])
            print(user.id)
            # data['user'] = email.id

            if data['first_name']:
                user.first_name = data['first_name']
            if data['last_name']:
                user.last_name = data['last_name']
            if data['phone']:
                user.phone = data['phone']
            if data['bio']:
                user.bio = data['bio']
            if data['dob']:
                user.dob = data['dob']
            if data['profile']:
                user.profile = data['profile']
            user.save()
            



        tutor_serializer = TutorSerializer(data=data)

        if tutor_serializer.is_valid():

            try:
                tutor = tutor_serializer.save()
                print('created ',tutor)
                print(tutor_serializer.data)

                return Response(tutor_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                print('Exeption', e)
                return Response({'error' : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            print('Errors', tutor_serializer.errors)
            return Response(tutor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        