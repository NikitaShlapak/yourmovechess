from django.core.management import BaseCommand
from competition.models import CustomUser, Activity


class Command(BaseCommand):
    help = "Marking all finalists"
    application_mode = False
    def handle(self, *args, **options):
        users = CustomUser.objects.filter(is_banned=False, is_active=True, not_plaing=False).order_by('place')
        girls_remaining = 44
        for user in users:
            try:
                Activity.objects.create(
                    user = user,
                    heading = 'Участник завершил отборочные этапы',
                    content = f"{user.get_full_name()} завершил(а) отборочные турниры на {user.place} месте с результатом {user.res1+user.res2} очков из 22 возможных.",
                    type = Activity.Types.STAGE_FINISHED
                )
                user.state = user.States.PASSED
                user.save()
            except:
                print(f"Unexpected error with {user=}")
            else:
                print(f"{user.get_full_name()} завершил отборочные этапы")
                print(user.place, user.gender, girls_remaining)
                if user.place <= 200 or (user.gender == user.Gender.F and girls_remaining>0):
                    print('Участник прошёл в финал.')
                    if user.gender == user.Gender.F:
                        girls_remaining = girls_remaining-1
                    try:
                        Activity.objects.create(
                            user=user,
                            heading='Участник прошёл в финал.',
                            content=f"{user.get_full_name()} получает приглашение в заочный финал",
                            type = Activity.Types.PROMOTED
                        )
                        user.state = user.States.FINAL_ACCEED
                        user.save()
                    except:
                        print(f"Unexpected error with {user=}")


