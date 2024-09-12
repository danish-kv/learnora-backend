from django.db import models
from user_profile.models import Tutor
from users.models import CustomUser
from course.models import Category
from base.base_models import BaseModel
from django.utils.text import slugify

# Create your models here.

class Contest(BaseModel):

    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('finished', 'Finished'),
    )

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, null=True, blank=True, related_name='contests')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='contests')
    slug = models.SlugField(max_length=250, unique=True, null=True)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    total_questions = models.IntegerField(default=0)
    max_points = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    difficulty_level = models.CharField(blank=True)
    time_limit = models.DurationField(null=True, blank=True, help_text="Time limit for contest participation (e.g., 00:10:00 for 10 minutes).")
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='scheduled')
    participants = models.ManyToManyField(CustomUser, through='Participant', blank=True)
    is_active = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if not self.slug or Contest.objects.filter(pk=self.pk, name=self.name).exists() == False:
            base_slug = slugify(self.name)
            slug = base_slug
            num = 1
            while Contest.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{num}'
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
    


class Question(BaseModel):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='questions', null=True)
    question_text = models.TextField()

    def __str__(self) -> str:
        return self.question_text
    

class Option(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', null=True)
    option_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.option_text
    

class Participant(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contest_participants', null=True)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='contest_participants', null=True)
    score = models.IntegerField(default=0)
    time_taken = models.DurationField(blank=True, null=True)
    completed_at = models.DateTimeField(null=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.contest.name}"



class Submission(BaseModel):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE , related_name='submissions', null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE , related_name='submissions', null=True)
    selected_option =  models.ForeignKey(Option, on_delete=models.CASCADE, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.participant.user.username} - {self.question.question_text}"



class Leaderboard(BaseModel):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='leaderboards', null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='leaderboards',null=True)
    score = models.IntegerField(default=0)
    rank = models.IntegerField(null=True)

    class Meta:
        unique_together = ('contest', 'user')

    def __str__(self) -> str:
        return f"{self.user.username} - {self.contest.name} - Rank : {self.rank}"
    

