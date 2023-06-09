# Generated by Django 4.1 on 2022-11-23 19:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0004_rename_rf_fide_customuser_fide_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='heading',
            field=models.CharField(blank=True, max_length=200, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='content',
            field=models.TextField(verbose_name='Содержание'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
