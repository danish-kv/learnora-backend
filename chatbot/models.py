from django.db import models
from users.models import CustomUser
from base.base_models import BaseModel
# Create your models here.

class Conversation(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='conversation')

class Message(BaseModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at']