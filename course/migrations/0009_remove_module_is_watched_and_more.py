# Generated by Django 5.1 on 2024-09-02 18:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0008_rename_level_course_skill_level'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='module',
            name='is_watched',
        ),
        migrations.AddField(
            model_name='studentcourseprogress',
            name='watched_modules',
            field=models.ManyToManyField(blank=True, related_name='watched_by_students', to='course.module'),
        ),
        migrations.AlterField(
            model_name='studentcourseprogress',
            name='last_accessed_module',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_progress', to='course.module'),
        ),
    ]
