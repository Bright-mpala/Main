import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Main.settings")
django.setup()  # Make sure this comes BEFORE any imports that rely on Django apps

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import core.routing

from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(core.routing.websocket_urlpatterns)
    ),
})
