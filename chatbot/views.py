from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .utils import get_gemini_response

# Create your views here.

class ConversactionViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        print(request.data)
        conversation = self.get_object()
        user_message = request.data.get('message')

        if not user_message:
            return Response({'error', 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_message_obj = Message.objects.create(conversation=conversation, content=user_message, is_user=True)
        
        ai_response = get_gemini_response(user_message)
        
        ai_message_obj = Message.objects.create(conversation=conversation, content=ai_response, is_user=False)
        
        return Response({
            'user_message': MessageSerializer(user_message_obj).data,
            'ai_message': MessageSerializer(ai_message_obj).data
        })
    
    def get_queryset(self):
        queryset = Conversation.objects.filter(user=self.request.user)
        return queryset