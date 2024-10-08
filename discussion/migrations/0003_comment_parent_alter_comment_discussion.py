# Generated by Django 5.1 on 2024-09-06 11:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discussion', '0002_rename_content_discussion_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='discussion.comment'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='discussion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commented_discussion', to='discussion.discussion'),
        ),
    ]
