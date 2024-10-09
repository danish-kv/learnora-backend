from django.db import models
from users.models import CustomUser



# Tutor model to store information about tutors, including status, CV, and basic profile details.
class Tutor(models.Model):
    VERIFIED = 'Verified'
    REQUESTED = 'Requested'
    PENDING = 'Pending'
    REJECTED = 'Rejected'

    STATUS_CHOICES = [
        (VERIFIED, 'verified'),
        (REQUESTED, 'requested'),
        (PENDING, 'pending'),
        (REJECTED, 'rejected'),
    ]

    # Linking the tutor profile to the CustomUser model
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='tutor_profile', null=True)
    cv = models.FileField(upload_to='cv/', blank=True, null=True)  # Field for uploading a tutor's CV
    display_name = models.CharField(max_length=100, null=True, blank=True)  # Name displayed on the profile
    headline = models.CharField(max_length=100, null=True, blank=True)  # Short headline or tagline for the tutor
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)  # Tutor's verification status
    
    def __str__(self):
        """String representation of the Tutor object."""
        return self.display_name or "Tutor"
    

# Experience model to capture a tutor's work experience details
class Experience(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='experiences', null=True)
    company_name = models.CharField(max_length=150,null=True, blank=True) # Name of the company where tutor worked
    position = models.CharField(max_length=150, null=True, blank=True) # Position held at the company
    start_date = models.DateField(null=True, blank=True)  # Start date of the work experience
    end_date = models.DateField(null=True, blank=True)  # End date of the work experience 

    def __str__(self):
        """String representation of the Experience object."""
        return f"{self.tutor} at {self.company_name}"
    

# Education model to capture a tutor's educational qualifications
class Education(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='education', null=True)
    highest_qualification = models.CharField(max_length=150, blank=True)  # Highest qualification attained
    name_of_institution = models.CharField(max_length=150, blank=True)  # Name of the educational institution
    year_of_qualification = models.DateField(null=True, blank=True)  # Year of graduation or qualification

    def __str__(self):
        """String representation of the Education object."""
        return f"{self.highest_qualification} from {self.name_of_institution}"


# Skill model to capture a tutor's specific skills
class Skill(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='skills', null=True)
    skill_name = models.CharField(max_length=100, blank=True)  # Name of the skill

    def __str__(self):
        """String representation of the Skill object."""
        return self.skill_name
