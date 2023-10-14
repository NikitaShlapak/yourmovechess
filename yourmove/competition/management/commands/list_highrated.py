from django.core.management import BaseCommand
from competition.models import CustomUser


class Command(BaseCommand):
    help = "Getting all users with rating over 2200"
    application_mode = False
    def handle(self, *args, **options):
        users = CustomUser.objects.filter(is_banned=False, is_active=True, not_plaing=False)
        for user in users:
            if user.get_max_rating()>=2200:
                print(f"{user.get_full_name()} ({user.email}, {user.lichess_nick}) - {user.get_max_rating()}")
