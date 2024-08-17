from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
    

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'student'


class IsTutor(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'tutor'
    

class IsTutorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return ( request.user and (request.user.is_superuser or request.user.role == 'tutor'))