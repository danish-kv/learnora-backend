from .models import Community, Message, Thread
from rest_framework import serializers
from users.api.user_serializers import UserSerializers






class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializers()
    is_my_message = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = '__all__'

    def get_is_my_message(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.sender == request.user
        return False


class CommunitySerializer(serializers.ModelSerializer):
    participants = UserSerializers(many=True)
    is_joined = serializers.SerializerMethodField()
    class Meta:
        model = Community
        fields = '__all__'

    def get_is_joined(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            return user in obj.participants.all()
        return False

class CreateCommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ['name', 'description', 'banner', 'max_participants']



class JoinCommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ['id']

    def save(self, **kwargs):
        print('community serailzer ...........')
        community = self.instance
        request = self.context.get('request')
        if request:
            user = request.user
            community.add_participant(user)

        