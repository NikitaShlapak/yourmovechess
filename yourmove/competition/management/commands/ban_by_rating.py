from django.core.management import BaseCommand
from competition.models import CustomUser, Activity


class Command(BaseCommand):
    help = "Getting all users with rating over 2300 and ban them"
    application_mode = False
    def handle(self, *args, **options):
        users = CustomUser.objects.filter(is_banned=False, is_active=True, not_plaing=False)
        for user in users:
            if user.get_max_rating()>2300:
                user.is_banned = True
                user.save()
                event = {
                    'heading': 'Участник дисквалифицирован',
                    'content': user.get_full_name() + ' был автоматически дисквалифицирован по причине слишком высокого рейтинга.',
                    'type': Activity.Types.BANNED,
                    'user': user
                }
                if user.gender == CustomUser.Gender.F:
                    event['content'] = event['content'].replace('был', 'была').replace('дисквалифицирован', 'дисквалифицирована')
                Activity.objects.create(**event)
                user.email_user(subject=f"Изменение статуса заявки", message=f"Вы были дисквалифицированы системой по причине слишком высокого рейтинга.")
                print(f'{user.get_full_name()} (id{user.pk}) is baned by rating')


