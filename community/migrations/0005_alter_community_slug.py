# Generated by Django 5.1 on 2024-10-10 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0004_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='community',
            name='slug',
            field=models.SlugField(max_length=250, null=True, unique=True),
        ),
    ]
