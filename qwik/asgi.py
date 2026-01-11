"""
ASGI config for qwik project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Import routing AFTER settings are set
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qwik.settings")

django_asgi_app = get_asgi_application()

import chats.routing

# Using type: ignore here is often necessary for the ProtocolTypeRouter 
# because it's a very dynamic Channels object
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chats.routing.websocket_urlpatterns
        )
    ),
})