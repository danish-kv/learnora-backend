import json
from channels.generic.websocket import  AsyncWebsocketConsumer
from .models import Community, Message, Notification
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
        print(f"Disconnecting from room group: {self.room_group_name}") 

        
    async def receive(self, text_data=None, bytes_data=None):
        print(f"Received data: {text_data}")

        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        user_id = text_data_json.get('user')
        message_type = text_data_json.get('type')
        print(message_type)
        print(text_data_json)
        print('llllllllllllllllllllllll')



        user = await self.get_user(user_id)
        
        if not user or not message:
            await self.send(text_data=json.dumps({
                'error' : 'Invalid message or user'
            }))
            return
        

        if message_type == 'video_call':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_call',
                    'message': message,
                    'user': user.username,
                    'userID': user.id,
                }
            )

        else:           
        
            print('userum message um nd')
            community = await self.get_community(self.slug)
            if community and user.is_authenticated:
                print('community user nddd')
                await self.save_message(community, user, message)
                print('message saved')
            
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'user': user.username,
                        'userID': user.id,
                    }
                )

                members = await self.get_community_members(community)
                notifications = [
                    Notification(
                        recipient=member,
                        community=community,
                        message=f'New message from {user.username}',
                        notification_type='new_message',
                        link=f'/community/{community.slug}/chat'
                    ) for member in members if member.id != user.id
                ]
                await self.create_notifications(notifications)

                for member in members:
                    if member.id != user.id:
                        await self.send_member_notification(
                            message=f'New message from {user.username}',
                            member=member,
                            community=community,
                        )


            else:
                await self.send(text_data=json.dumps({
                'error': 'User not authenticated or community not found'
                }))  
    

    async def send_member_notification(self, message, community, member):
        notification_data = {
            'type' : 'new_message',
            'message' : message,
            'community' : community,
            'link' : f'/community/{community.slug}/chat'
        }

        await self.create_notification(message, member, "new_message", community)

        await self.channel_layer.group_send(
            f'user_{member.id}',
            {
                'type': 'send_notification',
                'data': notification_data,
            }
        )



    async def chat_message(self, event):
        print('event', event)
        message = event['message']
        user = event['user']
        userID = event['userID']

        await self.send(text_data=json.dumps({
            'type': 'chat_message',  
            'content' : message,
            'user' : user ,
            'userID' : userID 
        }))

    async def video_call(self, event):
        print('Video call event:', event)
        message = event['message']
        user = event['user']
        userID = event['userID']

        await self.send(text_data=json.dumps({
            'type': 'video_call',  
            'message': message,
            'user': user,
            'userID': userID
        }))

    
    @database_sync_to_async
    def save_message(self, community, user, message):
        if not community or not user:
            print('Community not found, cannot save message')
            return None
        
        try:
            print(f'Saving message: {message} for user: {user} in community: {community}')
            return Message.objects.create(community=community, sender=user, content=message)
        except Exception as e :
            print(f'error {e}')
            return None
    
    @database_sync_to_async
    def get_community(self, slug):
        print('getting community')
        try:
            return Community.objects.get(slug=slug)
        except Community.DoesNotExist:
            return None
        
    @database_sync_to_async
    def get_user(self, user_id):
        print('getting user')
        try:
            return CustomUser.objects.get(id=user_id)
        except Exception as e:
            print('User is not found',e )
            return None
        
    

    @database_sync_to_async
    def get_community_members(self, community):
        return community.participants.all()



class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        if self.user.is_authenticated:
            self.group_name = f'user_{self.user.id}'

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            
        

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event['data']))


@database_sync_to_async
def create_notifications(notifications):
    Notification.objects.bulk_create(notifications)