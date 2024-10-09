from django.db import models
from users.models import CustomUser
from base.base_models import BaseModel

# Create your models here.

class Conversation(BaseModel):
    """
    Model representing a conversation between a user and the AI.

    A conversation is associated with a specific user and can contain multiple messages.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='conversations'  
    )

    def __str__(self):
        return f"Conversation with {self.user.username}"


class Message(BaseModel):
    """
    Model representing a message within a conversation.

    A message can either be from the user or the AI. Messages are ordered by their creation time.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'  # Related name to access messages from a conversation
    )
    content = models.TextField()  # Content of the message
    is_user = models.BooleanField(default=True)  # True if the message is from the user, False if from the AI

    class Meta:
        ordering = ['created_at'] 

    def __str__(self):
        return f"{'User' if self.is_user else 'AI'}: {self.content[:20]}..."  
