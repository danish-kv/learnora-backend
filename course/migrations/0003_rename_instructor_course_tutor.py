# Generated by Django 5.1 on 2024-08-17 05:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_remove_course_categories_course_category_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='instructor',
            new_name='tutor',
        ),
    ]
