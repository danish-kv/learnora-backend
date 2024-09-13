import json
from channels.generic.websocket import  AsyncWebsocketConsumer
from .models import Community, Message
from users.models import CustomUser
from channels.db import database_sync_to_async




class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("mooneee work aaaayi")
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.room_group_name = f'chat_{self.slug}'

        print(f"Connecting to room group: {self.room_group_name}")  


        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"Disconnecting from room group: {self.room_group_name}")  # Add logging

        
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        print('llllllllllllllllllllllll')
        message = text_data_json.get('message', '')
        user_id = text_data_json.get('user', None)

        user = await self.get_user(user_id)
        print(user)
        if user:
            print('yes user')
        else:
            print('nooooooooo')
        community = await self.get_community(self.slug)
        if community and user.is_authenticated:
            await self.save_message(community, user, message)
        

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': user.username,
                }
            )
        else:
            # Optionally handle cases where the user is not authenticated
            await self.send(text_data=json.dumps({
                'error': 'User not authenticated'
            }))    


    async def chat_message(self, event):
        message = event['message']
        user = event['user']


        await self.send(text_data=json.dumps({
            'message' : message,
            'user' : user 
        }))
    
    @database_sync_to_async
    def save_message(self, community, user, message):
        return Message.objects.create(community=community, sender=user, content=message)
    
    @database_sync_to_async
    def get_community(self, slug):
        try:
            return Community.objects.get(slug=slug)
        except Community.DoesNotExist:
            return None
        
    @database_sync_to_async
    def get_user(self, user_id):
        print('hola')
        try:
            return CustomUser.objects.get(id=user_id)
        except Exception as e:
            print('User is not found',e )
            return None
