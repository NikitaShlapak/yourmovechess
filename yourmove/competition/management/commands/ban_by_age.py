from django.core.management import BaseCommand
from competition.models import CustomUser


class Command(BaseCommand):
    help = "Updating gender of all users by the last letter of middle name"
    application_mode = False
    def handle(self, *args, **options):
        users = CustomUser.objects.filter(is_banned=False, is_active=True, not_plaing=False).exclude(b_date__year__lte=2007,b_date__year__gte=1988)
        print(f"Found {len(users)} users to ban")
        if len(users):
            for user in users:
                print(f'(id{user.pk}) {user.email} - {user.get_full_name()}: {user.b_date}')


