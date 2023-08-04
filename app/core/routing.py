from django.urls import path
from .wsconsumer_ping import PingWSConsumer

websocket_urlpatterns = [
    path("ws/com/ping/<int:user_id>/", PingWSConsumer.as_asgi()),
]
