import json
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from .models import Tutor, Skill, Education, Experience
from users.models import CustomUser
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import TutorSerializer
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from datetime import datetime
from .models import Tutor
from base.custom_permissions import IsAdmin, IsStudent, IsTutor, IsTutorOrAdmin
from django.db import transaction
# Create your views here.


class TutorProfile(APIView):
    permission_classes = [IsTutorOrAdmin]

    def post(self, request):
        
        print('before json')
        data = request.data.copy()  

        error = {}

        if 'first_name' in data:
            if not data['first_name']:
                error['First name'] = 'First name is required'

        if 'last_name' in data:
            if not data['last_name']:
                error['Last name'] = 'Last name is required'        

        try:
            validate_email(data['email'])
        except ValidationError:
            return Response({'error' : 'Invalid Email address'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if 'public_name' in data:
            if not data['public_name']:
                error['Public name'] = 'public name is required'

        if 'phone' in data:
            if not data['phone']:
                error['Phone'] = 'Phone is required'

        if 'phone' in data and not re.match(r'^\+?\d{10,15}$', data['phone']):
            if not data['phone']:
                error['Phone'] = 'Invalid phone number format'

        if 'headline' in data:
            if not data['headline']:
                error['Headline'] = 'Headline is required'

        if 'bio' in data:
            if not data['bio']:
                error['Bio'] = 'Bio is required'

        if 'profile' in data:
            if not data['profile']:
                error['profile'] = 'Profile is required'

        if 'dob' in data:
            try:
                dob = datetime.strptime(data['dob'], '%Y-%m-%d')

                if dob > datetime.now():
                    error['Date of Birth'] = 'Date of Birth cannot be in the future'

            except ValueError:
                error['Date of Birth'] = 'Invalid date format for DOB'

        if 'cv' in data:
            cv = data['cv']
            if not hasattr(cv,'file'):
                return Response({'error' : 'CV must be valid file'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            if 'education' in data:
                education_data = json.loads(data['education'])
                for edu in education_data:
                    if 'highestQualification' not in edu or not edu['highestQualification']:
                        error['Education'] = 'Each education entry must have a highest qualification'
                    if 'institute' not in edu or not edu['institute']:
                        error['Education'] = 'Each education entry must have a institution'
                    if 'year' not in edu or not edu['year']:
                        error['Education'] = 'Each education entry must have a year'
        except json.JSONDecodeError:
            return Response({'error' : 'Invalid JSON Format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # try:
        #     if 'experiences' in data:
        #         experiences_data = json.loads(data['experiences'])
        #         for exp in experiences_data:
        #             if 'Workplace' not in exp or not exp['Workplace']:
        #                 error['Workplace'] = 'Each experiences entry must have a company name'
        #             if 'position' not in exp or not exp['position']:
        #                 error['Position'] = 'Each experiences entry must have a position'
        #             if 'startDate' not in exp or not exp['startDate']:
        #                 error['Start Date'] = 'Each experiences  must have a start year'
        #             if 'endDate' not in exp or not exp['endDate']:
        #                 error['End Date'] = 'Each experiences  must have a end year'
        # except json.JSONDecodeError:
        #     return Response({'error' : 'Invalid JSON Format'}, status=status.HTTP_400_BAD_REQUEST)

        print('errors ===' , error)

        if error:
            return Response(data={'error' : error}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            if 'education' in data:
                data['education'] = json.loads(data['education'][0] if isinstance(data['education'], list) else data['education'])
            if 'experiences' in data:
                data['experiences'] = json.loads(data['experiences'][0] if isinstance(data['experiences'], list) else data['experiences'])
            if 'skills' in data and isinstance(data['skills'], list) and len(data['skills']) == 1:
                data['skills'] = data['skills'][0].split(',')  
        except json.JSONDecodeError as e:
            return Response({'error': f'Invalid JSON: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        print('after tutor profile',data)

        if 'email' in data:
            print(data['email'])
            try:
                user = CustomUser.objects.get(email=data['email'])

            except CustomUser.DoesNotExist:
                return Response(data={'error' : 'User not Found'}, status=status.HTTP_404_NOT_FOUND)
            print(user.id)
            data['user'] = user.id

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
                with transaction.atomic():
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
        


    def get(self, request):
        data = Tutor.objects.all().select_related('user')
        serializer = TutorSerializer(data, many=True)
            
        print(serializer.data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    


class TutorDetails(generics.RetrieveUpdateAPIView):
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
    permission_classes = [IsAdmin]






