from django.urls import path

from core.voice.consumers import AdminConsumer, PluginConsumer

websocket_urlpatterns = [
    path("ws/plugin/", PluginConsumer.as_asgi()),
    path("ws/admin/", AdminConsumer.as_asgi()),
]
