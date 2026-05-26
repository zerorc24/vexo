import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.contrib.auth.models import User
from .models import Room, Message

from messaging.utils.encryption import encrypt_message, decrypt_message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")

        user = self.scope["user"]

        # save to DB (ENCRYPT HERE)
        room = await self.get_room(self.room_name)
        msg_obj = await self.create_message(room, user, message)

        # broadcast decrypted message to UI (clean chat experience)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,   # send plain text to frontend
                "user": user.username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "user": event["user"],
        }))

    # --------------------
    # DB OPERATIONS
    # --------------------
    @database_sync_to_async
    def get_room(self, room_name):
        return Room.objects.get(name=room_name)

    @database_sync_to_async
    def create_message(self, room, user, message):
        # 🔐 ENCRYPT BEFORE SAVING
        encrypted_text = encrypt_message(message)

        return Message.objects.create(
            room=room,
            sender=user,
            content=encrypted_text
        )