# Generated by Django 4.1 on 2022-11-23 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0008_alter_activity_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='gender',
            field=models.TextField(choices=[('Male', 'Мужской'), ('Female', 'Женский')], default='Male', verbose_name='Пол'),
        ),
    ]
