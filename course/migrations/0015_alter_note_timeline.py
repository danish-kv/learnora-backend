# Generated by Django 5.1 on 2024-10-10 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0014_alter_transaction_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='timeline',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]