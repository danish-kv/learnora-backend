from django.db import models
from users.models import CustomUser

# Create your models here.


class Tutor(models.Model):
    VERIFIED = 'verified'
    PENDING = 'pending'
    DECLINED = 'declined'

    STATUS_CHOICES = [
        (VERIFIED, 'Verified'),
        (PENDING, 'Pending'),
        (DECLINED, 'Declined'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='tutor_profile', null=True)
    cv = models.FileField(upload_to='cv/', blank=True, null=True)
    display_name = models.CharField(max_length=100, null=True, blank=True)
    headline = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES, default=PENDING)
    def __str__(self):
        return self.display_name  or "Tutor"  
    
    
class Experience(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='experiences', null=True)
    company_name = models.CharField(max_length=150,null=True, blank=True)
    position = models.CharField(max_length=150, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.tutor} at {self.company_name}"


class Education(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='education', null=True)
    highest_qualification = models.CharField(max_length=150, blank=True)
    name_of_institution = models.CharField(max_length=150, blank=True)
    year_of_qualification = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.highest_qualification} from {self.name_of_institution}"


class Skill(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='skills', null=True)
    skill_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.skill_name