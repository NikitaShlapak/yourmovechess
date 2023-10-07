from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.core.management import BaseCommand

from competition.models import CustomUser


class Command(BaseCommand):
    help = "Sending hardcoded message"
    application_mode = False
    def handle(self, *args, **options):
        users = CustomUser.objects.filter(is_banned=False)
        recipient_list = [user.email for user in users]
        send_mail(subject='Участие в проекте "Ход за тобой".',
                  recipient_list=recipient_list,
                  message="""Уважаемый участник! Вы зарегистрировались на портале https://yourmovechess.ru/ и тем самым подали заявку на Всероссийский проект "Ход за тобой". 
Проверка заявок окончена и уже сегодня в 14:00 по МСК начнётся первый турнир. Если Вы ранее прикрепили свой аккаунт lichess.org, то вы уже были добавлены в клуб (https://lichess.org/team/KZOBTBjG) и все турниры.
Если нет, то поторопитесь, иначе опоздаете!
Убедительная просьба - заранее покиньте те, в которых точно не планируете участвовать.
Удачи в играх!""", from_email=EMAIL_HOST_USER)