from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser
from django.db.models import Q
from users.api.user_serializers import UserSerializers
from rest_framework.viewsets import ModelViewSet, ViewSet
from course.models import Course, Category
from course.serializers import CourseSerializer, CategorySerializer
from base.custom_permissions import IsAdmin, IsTutor
from course.models import Course, StudentCourseProgress, Transaction, Module, Review
from django.db.models import Sum, Count
from course.serializers import TransactionSerializer, ReviewSerializer, StudentCourseProgressSerializer
from contest.models import Leaderboard
from contest.serializers import LeaderboardSerializer
from django.db.models.functions import TruncMonth

# Create your views here.

class StudentManageView(APIView):
    def get(self, request):
        student = CustomUser.objects.filter(Q (role='student') & Q(is_superuser=False))
        print('students' , student)
        seri = UserSerializers(student, many=True)
        print(seri.data)
        return Response(data=seri.data, status=status.HTTP_200_OK)
    
    def post (self, request, id=None):
        print(request.data)

        try:
            student = CustomUser.objects.get(id=id, role='student')
            status_value = request.data.get('value')
            if status_value == "block":
                student.status = False
                print('student blocked')
            elif status_value == 'unblock':
                student.status = True
                print('student unBlocked')
            student.save()
            print(student.status)
            return Response(data={"message" : "Status updated successfully" },status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response(data={'error' : 'student not found'}, status=status.HTTP_404_NOT_FOUND)
    




class RequestedCourses(ModelViewSet):
    queryset = Course.objects.filter(status='Requested')
    serializer_class = CourseSerializer
    permission_classes = [IsAdmin]


class RequestedCategory(ModelViewSet):
    queryset = Category.objects.filter(status='Requested')
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin | IsTutor]

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'tutor_profile'):
            serializer.save(status='Requested')






class AdminDashboardView(ViewSet):
    permission_classes = [IsAdmin]

    def list(self, request):
        total_course = Course.objects.count()
        enrolled_course = StudentCourseProgress.objects.count()
        total_amount = Transaction.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_views = Module.objects.aggregate(total_view_count=Sum('views_count'))['total_view_count'] or 0

        completed_course = StudentCourseProgress.objects.filter(progress='Completed').count()
        ongoing_course = StudentCourseProgress.objects.filter(progress='Ongoing').count()
        not_started_course = StudentCourseProgress.objects.filter(progress='Not Started').count()      

        recent_purchase = Transaction.objects.order_by('-id')[:5]
        recent_purchase_serializer = TransactionSerializer(recent_purchase, many=True)

        review_data = Review.objects.order_by('-id')[:5]
        review_data_serializer = ReviewSerializer(review_data, many=True, context={'request': request})

        recent_enrollment = StudentCourseProgress.objects.order_by('-created_at')[:5]
        recent_enrollment_serializer = StudentCourseProgressSerializer(recent_enrollment, many=True, context={'request': request})

        recent_contest = Leaderboard.objects.order_by('-created_at')[:5] 
        recent_contest_serializer = LeaderboardSerializer(recent_contest, many=True)

        monthly_enrollments = ( StudentCourseProgress.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month'))

        enrollment_data = [0] * 12
        for entry in monthly_enrollments:
            month = entry['month'].month - 1
            enrollment_data[month] = entry['count']

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
            "enrollment_data" : enrollment_data
        }

        return Response(response_data, status=status.HTTP_200_OK)
