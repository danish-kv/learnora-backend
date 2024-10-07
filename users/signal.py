import pyotp
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import CustomUser
from user_profile.models import Tutor


def generate_otp():
    """
    Generate a one-time password (OTP) using TOTP (Time-based One-Time Password).
    
    Returns:
        str: A 5-digit OTP code.
    """
    # Create a TOTP instance with a random base32 key
    totp = pyotp.TOTP(pyotp.random_base32())
    # Get the current OTP
    otp = totp.now()
    # Return the first 5 characters of the OTP
    return otp[:5]


def send_otp_email(email, otp):
    """
    Send an OTP code to a specified email address.
    
    Args:
        email (str): The recipient's email address.
        otp (str): The OTP code to send.
    """
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}'  # Message content
    email_from = settings.EMAIL_HOST_USER  # Sender's email from settings
    recipient_list = [email]  # List of recipients
    # Send the email
    send_mail(subject, message, email_from, recipient_list)


@receiver(post_save, sender=CustomUser)
def generate_and_send_otp(sender, instance, created, **kwargs):
    """
    Signal receiver that generates and sends an OTP when a new CustomUser is created.
    
    Args:
        sender: The model class (CustomUser).
        instance: The instance of the model being saved.
        created (bool): Indicates if a new record was created.
        **kwargs: Additional keyword arguments.
    """
    if created:
        otp = generate_otp()  # Generate the OTP
        instance.otp = otp  # Assign the OTP to the user instance
        instance.save()  # Save the instance with the OTP
        send_otp_email(instance.email, otp)  # Send the OTP email


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a Tutor profile when a new CustomUser with the role 'tutor' is created.
    
    Args:
        sender: The model class (CustomUser).
        instance: The instance of the model being saved.
        created (bool): Indicates if a new record was created.
        **kwargs: Additional keyword arguments.
    """
    if created and instance.role == 'tutor':
        # Create a Tutor profile for the newly created user
        Tutor.objects.create(user=instance)

