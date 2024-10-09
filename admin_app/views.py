from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth
from rest_framework.viewsets import ModelViewSet, ViewSet
from datetime import datetime

from users.models import CustomUser
from users.api.user_serializers import UserSerializers
from course.models import Course, Category, StudentCourseProgress, Transaction, Module, Review
from course.serializers import (
    CourseSerializer, 
    CategorySerializer, 
    TransactionSerializer, 
    ReviewSerializer, 
    StudentCourseProgressSerializer
)
from base.custom_permissions import IsAdmin, IsTutor
from contest.models import Leaderboard
from contest.serializers import LeaderboardSerializer
from user_profile.serializers import CourseSalesSerializer


# View for managing student accounts
class StudentManageView(APIView):
    """
    API view for managing student accounts by admins.
    Allows blocking/unblocking of students.
    """

    def get(self, request):
        """
        Retrieve a list of  studnets 
        """
        students = CustomUser.objects.filter(Q(role='student') & Q(is_superuser=False))
        serializer = UserSerializers(students, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, id=None):
        """
        Block or unblock a student based on the request data
        """
        try:
            student = CustomUser.objects.get(id=id, role='student')
            status_value = request.data.get('value')

            if status_value == "block":
                student.status = False
            elif status_value == "unblock":
                student.status = True

            student.save()
            return Response(data={"message": "Status updated successfully"}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response(data={'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


# ViewSet for managing courses with 'Requested' status
class RequestedCourses(ModelViewSet):
    """
    ViewSet for managing courses with 'Requested' status. 
    Only accessible by admins.
    """
    queryset = Course.objects.filter(status='Requested')
    serializer_class = CourseSerializer
    permission_classes = [IsAdmin]


# ViewSet for managing categories with 'Requested' status
class RequestedCategory(ModelViewSet):
    """
    ViewSet for managing categories with 'Requested' status.
    Accessible by admins and tutors.
    """
    queryset = Category.objects.filter(status='Requested')
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin | IsTutor]

    def perform_create(self, serializer):
        """
        Override the perform_create method to set the status as 'Requested' when created by a tutor.
        """
        if hasattr(self.request.user, 'tutor_profile'):
            serializer.save(status='Requested')


# ViewSet for admin dashboard data
class AdminDashboardView(ViewSet):
    """
    ViewSet for providing data for the admin dashboard.
    Includes stats on courses, enrollments, transactions, views, and recent activities.
    """
    permission_classes = [IsAdmin]

    def list(self, request):
        """
        Retrieve statistics and recent activities for the admin dashboard.
        """
        # Fetch stats
        total_courses = Course.objects.count()
        enrolled_courses = StudentCourseProgress.objects.count()
        total_amount = Transaction.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_views = Module.objects.aggregate(total_view_count=Sum('views_count'))['total_view_count'] or 0

        # Course progress stats
        completed_courses = StudentCourseProgress.objects.filter(progress='Completed').count()
        ongoing_courses = StudentCourseProgress.objects.filter(progress='Ongoing').count()
        not_started_courses = StudentCourseProgress.objects.filter(progress='Not Started').count()

        # Recent activities
        recent_purchases = Transaction.objects.order_by('-id')[:5]
        recent_reviews = Review.objects.order_by('-id')[:5]
        recent_enrollments = StudentCourseProgress.objects.order_by('-created_at')[:5]
        recent_contests = Leaderboard.objects.order_by('-created_at')[:5]

        # Serialize data
        recent_purchase_serializer = TransactionSerializer(recent_purchases, many=True)
        recent_review_serializer = ReviewSerializer(recent_reviews, many=True, context={'request': request})
        recent_enrollment_serializer = StudentCourseProgressSerializer(recent_enrollments, many=True, context={'request': request})
        recent_contest_serializer = LeaderboardSerializer(recent_contests, many=True)

        # Monthly enrollments for charting
        monthly_enrollments = (
            StudentCourseProgress.objects
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        enrollment_data = [0] * 12  # Initialize a list with 12 months
        for entry in monthly_enrollments:
            month = entry['month'].month - 1
            enrollment_data[month] = entry['count']

        # Prepare response data
        response_data = {
            "stats": {
                "total_courses": total_courses,
                "enrolled_courses": enrolled_courses,
                "total_amount": total_amount,
                "total_views": total_views
            },
            "progress": {
                "completed_courses": completed_courses,
                "ongoing_courses": ongoing_courses,
                "not_started_courses": not_started_courses
            },
            "recent_purchases": recent_purchase_serializer.data,
            "recent_reviews": recent_review_serializer.data,
            "recent_enrollments": recent_enrollment_serializer.data,
            "recent_contests": recent_contest_serializer.data,
            "enrollment_data": enrollment_data
        }

        return Response(response_data, status=status.HTTP_200_OK)


# ViewSet for generating admin sales reports
class AdminSalesReport(ViewSet):
    """
    ViewSet for generating sales reports for admin.
    Reports can be filtered by date range (start and end).
    """

    def list(self, request):
        """
        Generate and return a sales report based on the specified date range.
        """
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')

        if start_date and end_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', ''))
                end_date = datetime.fromisoformat(end_date.replace('Z', ''))

                # Fetch sales report data
                sales_report_data = (
                    Transaction.objects.filter(created_at__range=(start_date, end_date))
                    .values('course_id', 'course__title')
                    .annotate(total_sales=Count('id'), total_amount=Sum('amount'))
                )

                sales_report_serializer = CourseSalesSerializer(sales_report_data, many=True)
                return Response({"sales": sales_report_serializer.data}, status=status.HTTP_200_OK)

            except ValueError:
                return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Missing 'start' or 'end' date"}, status=status.HTTP_400_BAD_REQUEST)
