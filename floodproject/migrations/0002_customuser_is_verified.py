# Generated by Django 4.2.1 on 2024-12-08 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('floodproject', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
