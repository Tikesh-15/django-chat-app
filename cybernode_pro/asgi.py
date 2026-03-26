import os
import django
from django.core.asgi import get_asgi_application

# 1. सबसे पहले एनवायरनमेंट सेट करें
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cybernode_pro.settings')

# 2. Django को मैन्युअली सेटअप करें (यह सबसे ज़रूरी लाइन है)
django.setup()

# 3. अब बाकी चीजें इम्पोर्ट करें
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})