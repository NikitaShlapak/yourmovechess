# Generated by Django 4.1 on 2022-08-30 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0002_remove_customuser_reason_customuser_in_streamer_comp_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ['date'], 'verbose_name': 'Событие', 'verbose_name_plural': 'События'},
        ),
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
    ]
