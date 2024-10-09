import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Community, Message, Notification
from users.models import CustomUser
from channels.db import database_sync_to_async


class GroupChatConsumer(AsyncWebsocketConsumer):
    """Handles real-time group chat functionality."""

    async def connect(self):
        """Establish connection to the WebSocket and join the chat group."""
        print("Connecting to group chat")
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.room_group_name = f'chat_{self.slug}'
        print(f"Connecting to room group: {self.room_group_name}")

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        """Handle disconnection from the WebSocket."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"Disconnected from room group: {self.room_group_name}")

    async def receive(self, text_data=None, bytes_data=None):
        """Handle incoming messages from the WebSocket."""
        print(f"Received data: {text_data}")

        # Parse the incoming message
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        user_id = text_data_json.get('user')
        message_type = text_data_json.get('type')
        print(message_type)
        print(text_data_json)

        # Fetch the user based on the user_id
        user = await self.get_user(user_id)

        if not user or not message:
            await self.send(text_data=json.dumps({
                'error': 'Invalid message or user'
            }))
            return

        # Handle video call messages
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
            # Handle regular chat messages
            community = await self.get_community(self.slug)
            if community and user.is_authenticated:
                await self.save_message(community, user, message)
                print('Message saved')

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'user': user.username,
                        'userID': user.id,
                    }
                )

                # Fetch community members and create notifications
                members = await self.get_community_members(community)
                notifications = [
                    Notification(
                        recipient=member,
                        community=community,
                        message=f'New message from {user.username}',
                        notification_type='new_message',
                        link=f'/community/{community.slug}'
                    ) for member in members if member.id != user.id
                ]
                await self.create_notifications(notifications)

                # Send notifications to community members
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
        """Send a notification to a community member."""
        notification = Notification(
            recipient=member,
            community=community,
            message=message,
            notification_type='new_message',
            link=f'/community/{community.slug}'
        )
        print('Sending notification...')

        await self.create_notifications([notification])

        notification_data = {
            'type': 'new_message',
            'message': message,
            'community': community.slug,
            'link': f'/community/{community.slug}'
        }

        await self.channel_layer.group_send(
            f'user_{member.id}',
            {
                'type': 'send_notification',
                'data': notification_data,
            }
        )

    async def chat_message(self, event):
        """Send a chat message to WebSocket clients."""
        message = event['message']
        user = event['user']
        userID = event['userID']

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'content': message,
            'user': user,
            'userID': userID
        }))

    async def video_call(self, event):
        """Send a video call message to WebSocket clients."""
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
        """Save a message to the database."""
        if not community or not user:
            print('Community not found, cannot save message')
            return None

        try:
            print(f'Saving message: {message} for user: {user} in community: {community}')
            return Message.objects.create(community=community, sender=user, content=message)
        except Exception as e:
            print(f'Error saving message: {e}')
            return None

    @database_sync_to_async
    def get_community(self, slug):
        """Retrieve a community by its slug."""
        print('Fetching community')
        try:
            return Community.objects.get(slug=slug)
        except Community.DoesNotExist:
            return None

    @database_sync_to_async
    def get_user(self, user_id):
        """Retrieve a user by their ID."""
        print('Fetching user')
        try:
            return CustomUser.objects.get(id=user_id)
        except Exception as e:
            print('User not found:', e)
            return None

    @database_sync_to_async
    def get_community_members(self, community):
        """Retrieve all members of a community."""
        try:
            print('Fetching participants')
            return list(community.participants.all())
        except Exception as e:
            print(f'Error fetching participants: {e}')
            return []

    @database_sync_to_async
    def create_notifications(self, notifications):
        """Bulk create notifications in the database."""
        print('Creating notifications:', notifications)
        Notification.objects.bulk_create(notifications)


class NotificationConsumer(AsyncWebsocketConsumer):
    """Handles real-time notification functionality for users."""

    async def connect(self):
        """Establish connection to the WebSocket for notifications."""
        print('Connecting to notification WebSocket...')
        self.userID = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"user_{self.userID}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        """Handle disconnection from the notification WebSocket."""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        """Send notification data to WebSocket clients."""
        await self.send(text_data=json.dumps(event['data']))
