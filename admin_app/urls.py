from django.urls import path
from .views import StudnetManageView

urlpatterns = [
    path('students/', StudnetManageView.as_view(), name='student' ),
    path('students/<int:id>', StudnetManageView.as_view(), name='student-block' )
]
