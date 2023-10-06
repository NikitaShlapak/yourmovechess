from django.core.management import BaseCommand


from competition.models import CustomUser


class Command(BaseCommand):
    help = "Updating gender of all users by the last letter of middle name"
    application_mode = False
    def handle(self, *args, **options):
        users = CustomUser.objects.filter(middle_name__endswith='а', gender=CustomUser.Gender.M)
        if users:
            for user in users:
                user.gender = CustomUser.Gender.F
                user.save()
            print(f"Updated {len(users)} user(-s)")
        else:
            print('No users to update')

