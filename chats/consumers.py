import json
from typing import Optional, Dict, Any, cast
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Thread, Message
from accounts.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    me: User
    other_user_id: int
    room_name: str
    personal_group: str

    async def connect(self) -> None:
        user = self.scope.get('user')
        if user is None or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close()
            return
        
        self.me = cast(User, user)
        self.personal_group = f"user_{self.me.pk}"
        await self.channel_layer.group_add(self.personal_group, self.channel_name)

        url_kwargs = self.scope.get('url_route', {}).get('kwargs', {})
        target_id = url_kwargs.get('user_id')

        if target_id and int(target_id) != 0:
            self.other_user_id = int(target_id)
            ids = sorted([int(self.me.pk), self.other_user_id])
            self.room_name = f"chat_{ids[0]}_{ids[1]}"
            await self.channel_layer.group_add(self.room_name, self.channel_name)

        await self.accept()

    async def receive(self, text_data: Optional[str] = None, bytes_data: Optional[bytes] = None) -> None:
        if not text_data: return
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'message':
            msg_text = data.get('message', '')
            # Save message (and create thread if it's the first message)
            await self.save_message(self.other_user_id, msg_text)
            
            # Send to room
            await self.channel_layer.group_send(self.room_name, {
                "type": "chat_message",
                "message": msg_text,
                "sender_id": self.me.pk,
            })

            # Notify Recipient's Inbox (For rapid count update)
            recipient_group = f"user_{self.other_user_id}"
            await self.channel_layer.group_send(recipient_group, {
                "type": "inbox_update",
                "message": msg_text,
                "sender_id": self.me.pk,
            })

        elif action == 'typing':
            if hasattr(self, 'room_name'):
                await self.channel_layer.group_send(self.room_name, {
                    "type": "typing_indicator",
                    "is_typing": data.get('typing', False),
                    "user_id": self.me.pk
                })

    async def chat_message(self, event): await self.send(text_data=json.dumps(event))
    async def typing_indicator(self, event): await self.send(text_data=json.dumps(event))
    async def inbox_update(self, event): await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, other_user_id, text):
        other_user = User.objects.get(pk=other_user_id)
        u1, u2 = (self.me, other_user) if self.me.pk < other_user.pk else (other_user, self.me)
        # Thread is ONLY created here when a message is actually sent
        thread, _ = Thread.objects.get_or_create(first_user=u1, second_user=u2)
        thread.save() 
        return Message.objects.create(thread=thread, sender=self.me, text=text)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.personal_group, self.channel_name)
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)