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
Наши администраторы заканчивают проверку заявок и скоро начнётся первый турнир. Убедитесь, пожалуйста, что Вы подтвердили свой рейтинг и прикрепили аккаунт на lichess.org. Если всё это выполнено, то вы автоматически будете (а, возможно, и уже были) добавлены в клуб (https://lichess.org/team/KZOBTBjG) и турниры. Убедитесь и в этом тоже. 
При необходимости - вступите в турниры самостоятельно или покиньте те, в которых точно не планируете участвовать.
Удачи в играх!""", from_email=EMAIL_HOST_USER)