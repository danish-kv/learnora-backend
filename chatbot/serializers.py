from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.

    This serializer handles the serialization and deserialization
    of Message instances, allowing for easy conversion between
    Message objects and JSON data.
    """

    class Meta:
        model = Message
        fields = '__all__'  # Include all fields from the Message model


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.

    This serializer includes a nested MessageSerializer to provide
    a representation of related messages within a conversation.
    """

    messages = MessageSerializer(many=True, read_only=True)  # Include related messages in the output

    class Meta:
        model = Conversation
        fields = '__all__'  # Include all fields from the Conversation model
