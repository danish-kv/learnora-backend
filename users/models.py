from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self,email,username,password=None, **extra_fields):
        if not email:
            raise ValueError('The email feild must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        print('extra fields of create superuser',extra_fields)
        username=extra_fields.get('username', 'admin')
        print(username,email,password)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email=email, username=username, password=password, **extra_fields)




class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('tutor', 'Tutor'),
    ]

    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=150, unique=True)
    bio = models.TextField(blank=True)
    profile = models.ImageField(upload_to='profile/', null=True, blank=True)
    phone = models.CharField(max_length=13,  blank=True)
    otp = models.CharField(max_length=10, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='admin')
    is_verified = models.BooleanField(default=False)
    auth_provider=models.CharField(max_length=50, default='email')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.email



