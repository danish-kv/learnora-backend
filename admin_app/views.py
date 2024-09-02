from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser
from django.db.models import Q
from users.api.user_serializers import UserSerializers
from rest_framework.viewsets import ModelViewSet
from course.models import Course
from course.serializers import CourseSerializer
from base.custom_permissions import IsAdmin
# Create your views here.

class StudnetManageView(APIView):
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
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdmin]