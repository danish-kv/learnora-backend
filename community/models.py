from django.db import models
from base.base_models import BaseModel
from user_profile.models import Tutor
from users.models import CustomUser
from django.utils.text import slugify

# Create your models here.



class Community(BaseModel):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, null=True, related_name='tutor')
    slug = models.SlugField(max_length=250, null=True)
    name = models.CharField(max_length=100, unique=True, null=True)
    description = models.TextField(null=True, blank=True)
    banner = models.ImageField(upload_to='community', null=True)
    max_participants = models.IntegerField(null=True)
    participants = models.ManyToManyField(CustomUser, blank=True, related_name='communities_joined')

    
    def save(self, *args, **kwargs):
        if not self.slug or Community.objects.filter(pk=self.pk, name=self.name).exists() == False:
            base_slug = slugify(self.name)
            slug = base_slug
            num = 1
            while Community.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)


    def add_participant(self, user):
        if self.participants.count() < self.max_participants:
            self.participants.add(user)
        else:
            raise ValueError("Max participant limit reached")
    
    def exit_participant(self, user):
        if user in self.participants.all():
            self.participants.remove(user)
        else:
            raise ValueError("User is not a participant in this community")


    def __str__(self) -> str:
        return f"{self.tutor.user.username}'s {self.name}"



class Message(BaseModel):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='sent_messages')
    content = models.TextField(null=True)

    def __str__(self) -> str:
        return f'{self.sender.username} : {self.content[:30]}...'
    

class Thread(BaseModel):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, related_name='threads')
    name = models.CharField(max_length=100, null=True)
    participants = models.ManyToManyField(CustomUser, related_name='threads')

    def __str__(self) -> str:
        return f"{self.community.name} : {self.name}"
    


class Notification(BaseModel):
    NOTIFICATION_TYPES = (
        ('message', 'Message'),
        ('new_course', 'New Course')
    )
    
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    message = models.CharField(max_length=100, null=True, blank=True)
    notification_type = models.CharField(choices=NOTIFICATION_TYPES, max_length=20)
    link = models.URLField(null=True, blank=True) 
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.notification_type}"
