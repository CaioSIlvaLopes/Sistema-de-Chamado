import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from tickets.models import Tickets, ChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get room name (ticket_id) from URL
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            
            # Use 'user' from scope if available (authenticated session)
            # or fallback to sender_id from frontend for ephemeral checking
            user = self.scope.get('user')
            
            if message and self.room_name:
                # Save to DB if user is authenticated
                saved_message = None
                if user and user.is_authenticated:
                    saved_message = await self.save_message(self.room_name, user, message)
                
                # BroadCast
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender_id': user.id if (user and user.is_authenticated) else None,
                        'username': user.username if (user and user.is_authenticated) else "Anônimo"
                    }
                )
        except json.JSONDecodeError:
            pass

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender_id = event.get('sender_id', None)
        username = event.get('username', '')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'username': username
        }))

    @database_sync_to_async
    def save_message(self, ticket_id, user, message_text):
        try:
            ticket = Tickets.objects.get(id=ticket_id)
            return ChatMessage.objects.create(
                ticket=ticket,
                sender=user,
                message=message_text
            )
        except Tickets.DoesNotExist:
            return None
