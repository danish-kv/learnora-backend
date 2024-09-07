# Generated by Django 5.1 on 2024-09-06 18:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discussion', '0004_remove_discussion_downvoted_by_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discussion',
            name='downvote_count',
        ),
        migrations.RemoveField(
            model_name='discussion',
            name='upvote_count',
        ),
        migrations.AddField(
            model_name='discussion',
            name='downvoted_by',
            field=models.ManyToManyField(blank=True, related_name='downvoted_discussions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='discussion',
            name='upvoted_by',
            field=models.ManyToManyField(blank=True, related_name='upvoted_discussions', to=settings.AUTH_USER_MODEL),
        ),
    ]