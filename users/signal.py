from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pyotp
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import CustomUser
import random
from user_profile.models import Tutor


def generate_otp():
    totp = pyotp.TOTP(pyotp.random_base32())
    otp = totp.now()
    return otp[:5]


def send_otp_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    print('otp :', otp,'  ', email)
    send_mail(subject, message,email_from,recipient_list)


@receiver(post_save, sender=CustomUser)
def generate_and_send_otp(sender,instance, created, **kwargs):
    if created:
        otp = generate_otp()
        instance.otp = otp
        instance.save()
        send_otp_email(instance.email, otp)


@receiver(post_save, sender = CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'tutor':
            Tutor.objects.create(user=instance)
        # else:
        #     if hasattr(instance, 'tutor_profile'):
        #         instance.tutor_profile.save()






