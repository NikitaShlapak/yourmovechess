import berserk
from django.core.management import BaseCommand

from competition.utils.chess_utils import BetterTeam, BetterSwiss
from competition.models import CustomUser, Activity

from yourmove.config import LICHESS_DATA


class Command(BaseCommand):
    help = "Confirming all users with confirmed rating and account"
    application_mode = False
    def handle(self, *args, **options):
        users = CustomUser.objects.filter(is_banned=False,
                                          is_active=True,
                                          not_plaing=False,
                                          rf_id__isnull=False,
                                          lichess_token__contains='li',
                                          state=CustomUser.States.UNCONFIRMED)
        for user in users:
            user.state = CustomUser.States.CONFIRMED
            user.save()
            event = {
                'heading': 'Заявка принята',
                'content': user.get_full_name() + ' был допущен к отборочным соревнованиям.',
                'type': Activity.Types.PROMOTED,
                'user': user
            }
            Activity.objects.create(**event)
            user.email_user(subject=f"Изменение статуса заявки", message=f"Поздравляем, ваша заявка была одобрена!"
                                                                         f"Проверьте свой аккаунт на lichess.org (https://lichess.org/@/{user.lichess_nick}).")
            if user.has_valid_token():
                token = user.lichess_token
                try:
                    session = berserk.TokenSession(token)
                    client = BetterTeam(session=session)

                    message = '12345' * 7
                    password = LICHESS_DATA['team_password']

                    res = client.join(LICHESS_DATA['team_id'], message=message, password=password)
                    if res['ok']:

                        master_session = berserk.TokenSession(LICHESS_DATA['master_token'])
                        joined_res = master_session.post(
                            f'https://lichess.org/api/team/{LICHESS_DATA["team_id"]}/request/{user.lichess_nick.lower()}/accept')
                        print(f"User {user.email} added to team.")
                        try:
                            client = BetterSwiss(session=session)
                            res = []
                            for swiss in LICHESS_DATA['swiss_ids']:
                                try:
                                    res.append(client.join(swiss)['ok'])
                                except:
                                    print(f'Unable to join user {user} to {swiss=}')
                            if any(res):
                                event = {
                                    'heading': 'Участник присоединился к турниру',
                                    'content': user.get_full_name() + ' Включился в борьбу',
                                    'type': Activity.Types.PROMOTED,
                                    'user': user
                                }

                                Activity.objects.create(**event)
                                user.state = user.States.ACTIVE
                                user.save()
                                print(f"User {user.email} added to tournaments.")
                        except:
                            print(f"Failed to add user {user.email} to tournaments.")
                except:
                    print(f"Failed to add user {user.email} to team.")