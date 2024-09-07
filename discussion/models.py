from django.db import models
from base.base_models import BaseModel
from users.models import CustomUser

# Create your models here.


class Discussion(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='discussed_user')
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='discussion/', null=True, blank=True)
    upvoted_by = models.ManyToManyField(CustomUser, related_name='upvoted_discussions', blank=True)
    downvoted_by = models.ManyToManyField(CustomUser, related_name='downvoted_discussions', blank=True)

    def __str__(self) -> str:
        return f'{self.user.username} - discussion - {self.title}'
    

    @property
    def upvote_count(self):
        return self.upvoted_by.count()
    
    @property
    def downvote_count(self):
        return self.downvoted_by.count()

    def upvote(self, user):
        if user in self.downvoted_by.all():
            self.downvoted_by.remove(user)
        self.upvoted_by.add(user)

    def downvote(self, user):
        if user in self.upvoted_by.all():
            self.upvoted_by.remove(user)
        self.downvoted_by.add(user)
    

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
