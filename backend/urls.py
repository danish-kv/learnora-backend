
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/django', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    path('',include('users.urls')),
    path('',include('user_profile.urls')),
    path('', include('admin_app.urls')),
    path('', include('course.urls')),
    
]



urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)