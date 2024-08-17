from django.db import models
from users.models import CustomUser
from user_profile.models import Tutor
from django.core.validators import MinValueValidator, MaxValueValidator
from base.base_models import BaseModel
from django.utils.text import slugify

# Create your models here.


class Category(models.Model):
    name = models.CharField(unique=True, max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            num = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{num}'
                num +=1
            self.slug =slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name



class Course(BaseModel):

    STATUS_CHOICES = (
        ('Approved', 'approved'),
        ('Declined', 'declined'),
        ('Pending', 'pending'),
    )

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='instructed_courses')
    category = models.ForeignKey(Category, related_name='courses', on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    title = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    total_enrollment = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rental_duration = models.PositiveIntegerField(default=0, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{num}'
                num +=1
            self.slug =slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
    
    

class Module(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    video = models.FileField(upload_to='module_videos/', null=True, blank=True)
    notes = models.FileField(upload_to='module_notes/', null=True, blank=True)
    likes_count = models.IntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']
    

class StudentCourseProgress(BaseModel):
    PROGRESS_CHOICES = (
        ('Completed', 'completed'),
        ('Ongoing', 'ongoing'),
        ('Not Started', 'not_started')
    )

    ACCESS_TYPE_CHOICES = (
        ('Rental', 'rental'),
        ('Lifetime', 'lifetime'),
    )

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_progress')
    progress = models.CharField(max_length=20, choices=PROGRESS_CHOICES, default='Not Started')
    watch_time = models.IntegerField(default=0)  # Watch time in minutes
    last_accessed_module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES, default='Lifetime')
    access_expiry_date = models.DateField(null=True, blank=True)


    def __str__(self):
        return f'{self.student.username} - {self.course.title}'
    


class Review(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    feedback = models.TextField(null=True, blank=True)
    rating = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f'{self.user.username} - {self.course.title}'
    

class Note(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    timeline = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.module.title}'


class Comment(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.module.title}'



class Transaction(BaseModel):

    STATUS_CHOICES = (
        ('Pending', 'pending'),
        ('Completed', 'completed'),
        ('Failed', 'failed'),
    )

    ACCESS_TYPE_CHOICES = (
        ('Rental', 'rental'),
        ('Lifetime', 'lifetime'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reference_id = models.CharField(max_length=100, unique=True)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES, default='Lifetime')
    access_expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.course.title} - {self.amount}'
