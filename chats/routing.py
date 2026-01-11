from django.urls import path
from . import consumers

# We use # type: ignore because the linter expects a standard Django view,
# but Channels uses an ASGI application.
websocket_urlpatterns = [
    path('ws/chat/<int:user_id>/', consumers.ChatConsumer.as_asgi()), # type: ignore
]