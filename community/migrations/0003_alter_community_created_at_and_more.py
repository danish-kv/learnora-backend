# Generated by Django 5.1 on 2024-09-14 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0002_rename_contest_message_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='community',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='community',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='thread',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='thread',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]