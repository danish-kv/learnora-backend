from django.db import models
from base.base_models import BaseModel
from users.models import CustomUser

# Create your models here.


class Discussion(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='discussed_user')
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='discussion/', null=True, blank=True)
    upvote_count = models.PositiveIntegerField(default=0)
    downvote_count = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f'{self.user.username} - discussion - {self.title}'
    
    def upvote(self):
        self.upvote_count += 1
        self.save()

    def downvote(self):
        self.downvote_count -= 1
        self.save()
    

class Comment(BaseModel):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='commented_discussion')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} - {self.discussion.title}'
    
    @property
    def is_reply(self):
        return self.parent is not None
