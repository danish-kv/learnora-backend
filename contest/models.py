from django.db import models
from user_profile.models import Tutor
from users.models import CustomUser
from course.models import Category
from base.base_models import BaseModel
from django.utils.text import slugify

# Create your models here.

class Contest(BaseModel):
    """Model representing a contest, including its associated details and participants."""

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
    difficulty_level = models.CharField(blank=True, max_length=50)
    time_limit = models.DurationField(null=True, blank=True, help_text="Time limit for contest participation (e.g., 00:10:00 for 10 minutes).")
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, null=True)
    participants = models.ManyToManyField(CustomUser, through='Participant', blank=True)

    def save(self, *args, **kwargs):
        """Override save method to automatically generate a unique slug based on the contest name."""
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
        """Return the contest name as a string representation."""
        return self.name


class Question(BaseModel):
    """Model representing a question associated with a contest."""

    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='questions', null=True)
    question_text = models.TextField()

    def __str__(self) -> str:
        """Return the question text as a string representation."""
        return self.question_text


class Option(BaseModel):
    """Model representing an option for a question in a contest."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', null=True)
    option_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        """Return the option text as a string representation."""
        return self.option_text


class Participant(BaseModel):
    """Model representing a participant in a contest, including their score and time taken."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contest_participants', null=True)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='contest_participants', null=True)
    score = models.IntegerField(default=0)
    time_taken = models.DurationField(blank=True, null=True)
    completed_at = models.DateTimeField(null=True)

    def __str__(self) -> str:
        """Return a string representation of the participant's username and contest name."""
        return f"{self.user.username} - {self.contest.name}"


class Submission(BaseModel):
    """Model representing a submission made by a participant for a question in a contest."""

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='submissions', null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='submissions', null=True)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        """Return a string representation of the participant's username and the question text."""
        return f"{self.participant.user.username} - {self.question.question_text}"


class Leaderboard(BaseModel):
    """Model representing a leaderboard entry for a contest, including user scores and ranks."""

    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='leaderboards', null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='leaderboards', null=True)
    score = models.IntegerField(default=0)
    rank = models.IntegerField(null=True)

    class Meta:
        unique_together = ('contest', 'user')

    def __str__(self) -> str:
        """Return a string representation of the user's username, contest name, and rank."""
        return f"{self.user.username} - {self.contest.name} - Rank: {self.rank}"
