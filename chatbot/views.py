from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .utils import get_gemini_response


class ConversationViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing conversations and messages.

    Provides actions for creating, retrieving, updating, and deleting conversations,
    as well as sending messages to the AI and receiving responses.
    """

    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """
        Send a message to a conversation and receive a response from the AI.

        Args:
            request: The HTTP request object containing the message data.
            pk: The primary key of the conversation to which the message is sent.

        Returns:
            Response: A response containing the user message and AI response.
        """
        conversation = self.get_object()
        user_message = request.data.get('message')

        # Validate that a message was provided
        if not user_message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user message object
        user_message_obj = Message.objects.create(conversation=conversation, content=user_message, is_user=True)

        # Get AI response based on the user message
        ai_response = get_gemini_response(user_message)

        # Create the AI message object
        ai_message_obj = Message.objects.create(conversation=conversation, content=ai_response, is_user=False)

        # Return the serialized user and AI messages in the response
        return Response({
            'user_message': MessageSerializer(user_message_obj).data,
            'ai_message': MessageSerializer(ai_message_obj).data
        })

    def get_queryset(self):
        """
        Override the default queryset to filter conversations by the logged-in user.

        Returns:
            QuerySet: A queryset of conversations for the current user.
        """
        queryset = Conversation.objects.filter(user=self.request.user)
        return queryset
