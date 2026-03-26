import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URL se username ya room_id uthao
        self.room_name = self.scope['url_route']['kwargs']['username']
        
        # LOGIC: Agar room_name mein '_' hai ya bahut bada random string hai, toh wo Stranger Room ho sakta hai
        # Par sabse safe tarika ye hai ki hum check karein ki kya ye username dunya mein exist karta hai
        is_user = await self.is_real_user(self.room_name)

        if is_user:
            # --- DOSON WALI CHAT (PERSONAL) ---
            users = sorted([self.scope['user'].username, self.room_name])
            self.room_group_name = f"chat_{users[0]}_{users[1]}"
        else:
            # --- STRANGER CHAT (ROOM ID BASED) ---
            self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        sender_user = self.scope['user']
        
        # Room name se pata karo ki personal chat hai ya stranger
        is_user = await self.is_real_user(self.room_name)

        if is_user:
            # 1. Personal Chat: Block check aur Database save
            is_blocked = await self.check_if_blocked(sender_user.id, self.room_name)
            if not is_blocked:
                await self.save_message_to_db(message, self.room_name)
                await self.broadcast_message(message, sender_user.username)
            else:
                await self.send(text_data=json.dumps({
                    'message': '⚠️ [SYSTEM]: Message not delivered. You are blocked.',
                    'sender': 'System'
                }))
        else:
            # 2. Stranger Chat: Seedha broadcast (Save karne ki zaroorat nahi hoti stranger mein)
            if message:
                await self.broadcast_message(message, sender_user.username)

    async def broadcast_message(self, message, sender):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender']
        }))

    # --- DATABASE OPERATIONS ---

    @sync_to_async
    def is_real_user(self, name):
        return User.objects.filter(username=name).exists()

    @sync_to_async
    def check_if_blocked(self, sender_id, receiver_username):
        from .models import Profile
        try:
            receiver = User.objects.get(username=receiver_username)
            profile = Profile.objects.get(user=receiver)
            return profile.blocked_users.filter(id=sender_id).exists()
        except:
            return False

    @sync_to_async
    def save_message_to_db(self, message, receiver_username):
        from .models import Message
        try:
            receiver = User.objects.get(username=receiver_username)
            Message.objects.create(
                sender=self.scope['user'],
                receiver=receiver,
                content=message
            )
        except Exception as e:
            print(f"Error saving: {e}")