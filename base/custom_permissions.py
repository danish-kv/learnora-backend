from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        # Allow access if the user is authenticated and is a superuser (admin)
        return request.user and request.user.is_authenticated and request.user.is_superuser


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        # Allow access if the user is authenticated and their role is 'student'
        return request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'student'


class IsTutor(BasePermission):
    def has_permission(self, request, view):
        # Allow access if the user is authenticated and their role is 'tutor'
        return request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'tutor'
