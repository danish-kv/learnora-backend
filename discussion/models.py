from django.db import models
from base.base_models import BaseModel
from users.models import CustomUser
from django.db import transaction

# Models for discussion and comments

class Discussion(BaseModel):
    """
    Model representing a discussion post. It includes a user who posted the discussion,
    title, description, an optional photo, and many-to-many relationships for upvotes and downvotes.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='discussed_user')
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='discussion/', null=True, blank=True)
    upvoted_by = models.ManyToManyField(CustomUser, related_name='upvoted_discussions', blank=True)
    downvoted_by = models.ManyToManyField(CustomUser, related_name='downvoted_discussions', blank=True)

    def __str__(self) -> str:
        """
        String representation of the discussion instance.
        """
        return f'{self.user.username} - discussion - {self.title}'

    @property
    def upvote_count(self):
        """
        Returns the count of upvotes for the discussion.
        """
        return self.upvoted_by.count()

    @property
    def downvote_count(self):
        """
        Returns the count of downvotes for the discussion.
        """
        return self.downvoted_by.count()

    @transaction.atomic
    def upvote(self, user):
        """
        Handles the upvote logic for a discussion. If the user already upvoted, their vote is removed.
        If they had downvoted, the downvote is removed, and an upvote is added.
        """
        if user in self.upvoted_by.all():
            self.upvoted_by.remove(user)
        else:
            if user in self.downvoted_by.all():
                self.downvoted_by.remove(user)
            self.upvoted_by.add(user)

    @transaction.atomic
    def downvote(self, user):
        """
        Handles the downvote logic for a discussion. If the user already downvoted, their vote is removed.
        If they had upvoted, the upvote is removed, and a downvote is added.
        """
        if user in self.downvoted_by.all():
            self.downvoted_by.remove(user)
        else:
            if user in self.upvoted_by.all():
                self.upvoted_by.remove(user)
            self.downvoted_by.add(user)


class Comment(BaseModel):
    """
    Model representing a comment on a discussion. Comments can have replies (child comments), 
    allowing for nested discussions.
    """
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='commented_discussion')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        """
        String representation of the comment instance.
        """
        return f'{self.user.username} - {self.discussion.title}'

    @property
    def is_reply(self):
        """
        Returns True if the comment is a reply to another comment (i.e., has a parent).
        """
        return self.parent is not None