# Generated by Django 5.1 on 2024-09-01 12:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0006_alter_course_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='level',
            field=models.CharField(choices=[('Beginner', 'beginner'), ('Intermediate', 'intermediate'), ('Advanced', 'advanced')], default='Beginner', max_length=20),
        ),
        migrations.AddField(
            model_name='module',
            name='is_liked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='module',
            name='is_watched',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='module',
            name='likes_count',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='module',
            name='views_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='note',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_notes', to='course.module'),
        ),
    ]
