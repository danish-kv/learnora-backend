# Generated by Django 5.1 on 2024-08-08 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructor',
            name='cv',
            field=models.FileField(blank=True, null=True, upload_to='cv/'),
        ),
    ]
