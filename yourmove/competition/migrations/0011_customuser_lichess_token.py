# Generated by Django 4.1 on 2023-01-12 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0010_alter_activity_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='lichess_token',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
    ]
