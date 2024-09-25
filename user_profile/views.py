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
from base.custom_permissions import IsAdmin, IsStudent, IsTutor
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets
from rest_framework import views
from .serializers import SkillSerializer, EducationSerializer, ExperienceSerializer


from course.models import Course, StudentCourseProgress, Transaction, Module, Review
from django.db.models import Sum
from course.serializers import TransactionSerializer, ReviewSerializer, StudentCourseProgressSerializer
from contest.models import Leaderboard
from contest.serializers import LeaderboardSerializer
# Create your views here.




class TutorProfile(APIView):
    

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


        if 'email' in data:
            try:
                user = CustomUser.objects.get(email=data['email'])

            except CustomUser.DoesNotExist:
                return Response(data={'error' : 'User not Found'}, status=status.HTTP_404_NOT_FOUND)
            
            data['userId'] = user.id

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

                    return Response(tutor_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error' : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            return Response(tutor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        data = Tutor.objects.all().select_related('user')
        serializer = TutorSerializer(data, many=True)
        
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    


class TutorDetails(generics.RetrieveUpdateAPIView):
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
    permission_classes = [IsAdmin | IsTutor]

    def update(self, request, *args, **kwargs):
        
        instance = self.get_object()

        old_status = instance.status

        response = super().update(request, *args, **kwargs)

        new_status = request.data.get('status')
        print(old_status,new_status,  )

        if old_status != new_status:
            self.send_change_status_email(instance, new_status)
        return response


    def send_change_status_email(self, tutor, new_status):
        print(tutor, new_status)
        subject = 'Update on Your Application Status'
        if new_status == 'Verified':
            message = 'Congratulations! Your application has been accepted'
        elif new_status == 'Rejected':
            message = "We're sorry to inform you that your application has been rejected"
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [tutor.user.email],  
            fail_silently=False,
        )
    

class MyProfileViewSets(viewsets.ModelViewSet):
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
    permission_classes = [IsTutor]

    def get_queryset(self):
        return Tutor.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        print(request.data)
        return super().update(request, *args, **kwargs)
    




class SkillEditView(APIView):
    def patch(self, request,id, *args, **kwargs):
        print(request.data)
        skills_data = request.data.get('skills', [])
        tutor = request.user.tutor_profile
        for skill in skills_data:
            Skill.objects.filter(tutor=tutor, id=skill['id']).update(skill_name=skill['skill_name'])

        return Response({'success': 'Skills updated'})

        


class EducationEditView(views.APIView):
    def patch(self, request,id, *args, **kwargs):
        print(request.data)

        try:
            edu = Education.objects.get(id=id)
        except Education.DoesNotExist:
            return Response({'error' : 'Education not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EducationSerializer(edu, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class ExperienceEditView(views.APIView):
    def patch(self, request,id, *args, **kwargs):
        print(request.data)

        try:
            edu = Experience.objects.get(id=id)
        except Experience.DoesNotExist:
            return Response({'error' : 'Education not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ExperienceSerializer(edu, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class TutorDashboardView(viewsets.ViewSet):

    def list(self, request):
        tutor = request.user.tutor_profile
        total_course = Course.objects.filter(tutor=tutor).count()
        enrolled_course = StudentCourseProgress.objects.filter(course__tutor=tutor).count()
        total_amount = Transaction.objects.filter(course__tutor=tutor).aggregate(total=Sum('amount'))['total'] or 0
        total_views = Module.objects.filter(course__tutor=tutor).aggregate(total_view_count=Sum('views_count'))['total_view_count'] or 0

        completed_course = StudentCourseProgress.objects.filter(course__tutor=tutor, progress='Completed').count()
        ongoing_course = StudentCourseProgress.objects.filter(course__tutor=tutor, progress='Ongoing').count()
        not_started_course = StudentCourseProgress.objects.filter(course__tutor=tutor, progress='Not Started').count()      

        recent_purchase = Transaction.objects.filter(course__tutor=tutor).order_by('-id')[:5]
        recent_purchase_serializer = TransactionSerializer(recent_purchase, many=True)

        review_data = Review.objects.filter(course__tutor=tutor).order_by('-id')[:5]
        review_data_serializer = ReviewSerializer(review_data, many=True, context={'request' : request})

        recent_enrollment = StudentCourseProgress.objects.filter(course__tutor=tutor).order_by('-created_at')[:5]
        recent_enrollment_serializer = StudentCourseProgressSerializer(recent_enrollment, many=True, context={'request': request}) 


        recent_contest = Leaderboard.objects.filter(contest__tutor=tutor).order_by('created_at')[:5]
        recent_contest_serializer = LeaderboardSerializer(recent_contest, many=True) 


        response_data = {
            "stats": {
                "total_courses": total_course,
                "enrolled_courses": enrolled_course,
                "total_amount": total_amount,
                "total_views": total_views
            },
            "progress": {
                "completed_course": completed_course,
                "ongoing_course": ongoing_course,
                "not_started_course": not_started_course
            },
            "recent_purchase": recent_purchase_serializer.data,
            "recent_reviews": review_data_serializer.data,
            "recent_enrollments": recent_enrollment_serializer.data,
            "recent_contests": recent_contest_serializer.data,
        }


        return Response(response_data, status=status.HTTP_200_OK)


