from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser
from django.db.models import Q
from users.api.serializers import UserSerializers
# Create your views here.


class StudnetManageView(APIView):
    def get(self, request):
        student = CustomUser.objects.filter(Q (role='student') & Q(is_superuser=False))
        
        seri = UserSerializers(student, many=True)
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
    

class InstructorManageView(APIView):
    def get(self, request):
        instructor = CustomUser.objects.filter(Q (role='instructor') )
        print(instructor)
        
        seri = UserSerializers(instructor, many=True)
        return Response(data=seri.data, status=status.HTTP_200_OK)
    
    def post (self, request, id=None):
        print(request.data)

        try:
            instructor = CustomUser.objects.get(id=id, role='instructor')
            status_value = request.data.get('value')
            if status_value == "block":
                instructor.status = False
                print('instructor blocked')
            elif status_value == 'unblock':
                instructor.status = True
                print('instructor unBlocked')
            instructor.save()
            print(instructor.status)
            return Response(data={"message" : "Status updated successfully" },status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response(data={'error' : 'Instructor not found'}, status=status.HTTP_404_NOT_FOUND)

