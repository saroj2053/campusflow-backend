from django.urls import re_path

from compare_modules.automation_tool import socket_consumer

websocket_urlpatterns = [
    re_path(r"ws/updates", socket_consumer.Consumer.as_asgi()),
]