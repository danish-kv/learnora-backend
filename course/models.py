from django.db import models
from users.models import CustomUser
from user_profile.models import Tutor
from django.core.validators import MinValueValidator, MaxValueValidator
from base.base_models import BaseModel
from django.utils.text import slugify
from django.db.models import Avg


class Category(models.Model):
    """
    Represents a category for courses.

    Attributes:
        name (str): The name of the category.
        slug (str): A URL-friendly slug for the category.
        is_active (bool): Indicates if the category is active.
        status (str): The approval status of the category.
    """
    STATUS_FEILDS = (
        ('Requested', 'requested'),
        ('Approved', 'approved')
    )

    name = models.CharField(unique=True, max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_FEILDS, default='Approved')

    def save(self, *args, **kwargs):
        """Automatically generates a unique slug for the category."""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            num = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{num}'
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Returns the name of the category as its string representation."""
        return self.name


class Course(BaseModel):
    """
    Represents a course taught by a tutor.

    Attributes:
        tutor (Tutor): The tutor instructing the course.
        category (Category): The category of the course.
        slug (str): A unique slug for the course.
        title (str): The title of the course.
        description (str): A description of the course.
        thumbnail (ImageField): A thumbnail image for the course.
        total_enrollment (int): The total number of students enrolled.
        status (str): The approval status of the course.
        skill_level (str): The required skill level for the course.
        price (Decimal): The price of the course.
        rental_price (Decimal): The rental price of the course.
        rental_duration (int): Duration for which the course can be rented.
        is_active (bool): Indicates if the course is active.
    """
    STATUS_CHOICES = (
        ('Approved', 'approved'),
        ('Declined', 'declined'),
        ('Pending', 'pending'),
        ('Requested', 'requested'),
    )
    LEVEL_CHOICES = (
        ('Beginner', 'beginner'),
        ('Intermediate', 'intermediate'),
        ('Advanced', 'advanced'),
    )

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='instructed_courses')
    category = models.ForeignKey(Category, related_name='courses', on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    title = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    total_enrollment = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    skill_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Beginner')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rental_duration = models.PositiveIntegerField(default=0, null=True)
    is_active = models.BooleanField(default=True)

    @property
    def average_rating(self):
        """Calculates and returns the average rating of the course."""
        return self.reviews.aggregate(average_rating=Avg('rating'))['average_rating'] or 0

    def save(self, *args, **kwargs):
        """Automatically generates a unique slug for the course."""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while Course.objects.filter(slug=slug).exists():  # Fix the filter to Course
                slug = f'{base_slug}-{num}'
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        """Returns the title of the course as its string representation."""
        return self.title

    class Meta:
        ordering = ['-created_at']


class Module(BaseModel):
    """
    Represents a module within a course.

    Attributes:
        course (Course): The course to which the module belongs.
        title (str): The title of the module.
        description (str): A description of the module.
        video (FileField): A video file for the module.
        duration (int): Duration of the module.
        notes (FileField): Notes associated with the module.
        is_liked (bool): Indicates if the module is liked.
        likes_count (int): The number of likes the module has received.
        views_count (int): The number of views the module has received.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    video = models.FileField(upload_to='module_videos/', null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True, default=0)
    notes = models.FileField(upload_to='module_notes/', null=True, blank=True)
    is_liked = models.BooleanField(default=False)
    likes_count = models.PositiveBigIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        """Returns the title of the module as its string representation."""
        return self.title

    class Meta:
        ordering = ['id']


class StudentCourseProgress(BaseModel):
    """
    Tracks the progress of a student in a course.

    Attributes:
        student (CustomUser): The student whose progress is tracked.
        course (Course): The course for which progress is tracked.
        progress (str): The current progress status.
        watch_time (int): Total watch time for the course.
        last_accessed_module (Module): The last module accessed by the student.
        access_type (str): The type of access for the course.
        access_expiry_date (date): The expiry date of access.
        liked_modules (ManyToManyField): Modules liked by the student.
        watched_modules (ManyToManyField): Modules watched by the student.
    """
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
    watch_time = models.IntegerField(default=0)  
    last_accessed_module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_progress')
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES, default='Lifetime')
    access_expiry_date = models.DateField(null=True, blank=True)
    liked_modules = models.ManyToManyField(Module, related_name='liked_video', blank=True)
    watched_modules = models.ManyToManyField(Module, related_name='watched_video', blank=True)

    def __str__(self):
        """Returns a string representation of the student's progress in the course."""
        return f'{self.student.username} - {self.course.title}'


class Review(BaseModel):
    """
    Represents a review of a course by a student.

    Attributes:
        course (Course): The course being reviewed.
        user (CustomUser): The user who wrote the review.
        feedback (str): Feedback provided by the user.
        rating (int): Rating given by the user.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    feedback = models.TextField(null=True, blank=True)
    rating = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        """Returns a string representation of the review."""
        return f'{self.user.username} - {self.course.title}'


class Note(BaseModel):
    """
    Represents a note created by a student for a specific module.

    Attributes:
        user (CustomUser): The user who created the note.
        module (Module): The module for which the note is created.
        content (str): The content of the note.
        timeline (str): A timeline for the note.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='student_notes')
    content = models.TextField(null=True, blank=True)
    timeline = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        """Returns a string representation of the note."""


class Transaction(BaseModel):
    """
    Represents a financial transaction for a course.

    Attributes:
        user (CustomUser): The user who made the transaction.
        course (Course): The course related to the transaction.
        amount (Decimal): The amount of the transaction.
        transaction_date (date): The date when the transaction was made.
        status (str): The current status of the transaction.
        reference_id (str): A unique identifier for the transaction.
        access_type (str): The type of access granted for the course.
        access_expiry_date (date): The expiry date of access for rental transactions.
    """
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
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reference_id = models.CharField(max_length=100, unique=True)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES, default='Lifetime')
    access_expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        """Returns a string representation of the transaction details."""
        return f'{self.user.username} - {self.course.title} - {self.amount}'
