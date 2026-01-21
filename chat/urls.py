from django.urls import path
from . import views

urlpatterns = [
    path('get/<int:ticket_id>/', views.get_chat_messages, name='get_chat_messages'),
    path('send/<int:ticket_id>/', views.send_chat_message, name='send_chat_message'),
    path('<str:room_name>/', views.chat_room, name='chat_room'),
    path('', views.chat_room, name='chat_index'),
    path('mensagem/<int:message_id>/anexo/', views.view_chat_attachment, name='view_chat_attachment'),
]
