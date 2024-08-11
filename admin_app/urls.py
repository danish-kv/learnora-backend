from django.urls import path
from .views import StudnetManageView, InstructorManageView

urlpatterns = [
    path('students/', StudnetManageView.as_view(), name='student' ),
    path('students/<int:id>', StudnetManageView.as_view(), name='student-block' ),
    path('instructors/', InstructorManageView.as_view(), name='instructor' ),
    path('instructors/<int:id>', InstructorManageView.as_view(), name='instructor-block' ),
]
