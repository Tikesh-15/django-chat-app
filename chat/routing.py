from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Regex ko thoda expand kiya hai taaki room_id aur usernames dono handle ho jayein
    re_path(r'ws/chat/(?P<username>[\w.@+-]+)/$', consumers.ChatConsumer.as_asgi()),
]