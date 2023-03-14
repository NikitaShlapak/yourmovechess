# Generated by Django 4.1 on 2022-11-23 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0006_alter_activity_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='type',
            field=models.TextField(choices=[('Rejected', 'Заявка отклонена'), ('Registered', 'Пользователь Зарегистрирован'), ('Banned', 'Участник дисквалифицирован'), ('Stage finished', 'Участник закончил отборочный этап'), ('Promoted', 'Участник переведён в следующий этап')], verbose_name='Тип события'),
        ),
    ]
