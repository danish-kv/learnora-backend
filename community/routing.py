from django.urls import re_path
from .consumers import GroupChatConsumer, NotificationConsumer

print('hey there in routes')

websocket_urlpatterns = [
    re_path(r'^ws/community/(?P<slug>[\w-]+)/$', GroupChatConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),  
]