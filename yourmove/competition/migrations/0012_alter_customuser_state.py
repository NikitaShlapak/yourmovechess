# Generated by Django 4.1 on 2023-01-12 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0011_customuser_lichess_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='state',
            field=models.TextField(choices=[('Отклонено', 'Заявка отклонена'), ('На проверке', 'Проверка не окончена'), ('Проверка пройдена', 'Участник допущен к отборочному этапу'), ('Этап 1', 'Участник допущен к этапу 1'), ('Этап 1 (завершён)', 'Участник завершил этап 1'), ('Этап 2', 'Участник допущен к этапу 2'), ('Этап 2 (завершён)', 'Участник завершил этап 2'), ('Этап 3', 'Участник допущен к этапу 3'), ('Этап 3 (завершён)', 'Участник завершил этап 3'), ('Суперфинал', 'Участник приглашён на очный суперфинал')], default='На проверке', verbose_name='Статус участника'),
        ),
    ]
