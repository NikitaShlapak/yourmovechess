import berserk
from django.core.management import BaseCommand
from competition.models import CustomUser, Activity
from competition.utils.chess_utils import BetterTeam, BetterSwiss
from yourmove.config import LICHESS_DATA


class Command(BaseCommand):
    help = "Adding all marked finalists to tournament"
    application_mode = False
    def handle(self, *args, **options):
        users = CustomUser.objects.filter(is_banned=False, is_active=True, not_plaing=False, state=CustomUser.States.FINAL_ACCEED).order_by('place')
        for user in users:
            if user.has_valid_token():
                token = user.lichess_token

                session = berserk.TokenSession(token)
                client = BetterTeam(session=session)

                message = '12345' * 7
                password = LICHESS_DATA['team_password']
                try: 
                    res = client.join(LICHESS_DATA['team_id'], message=message, password=password)
                except:
                    print(f"unable to add user {user} to team")
                if res['ok']:
                    master_session = berserk.TokenSession(LICHESS_DATA['master_token'])
                    joined_res = master_session.post(
                        f'https://lichess.org/api/team/{LICHESS_DATA["team_id"]}/request/{user.lichess_nick.lower()}/accept')
                    print(f"User {user.email} added to team.")
                    try:
                        client = BetterSwiss(session=session)
                        try:
                            res=client.join(LICHESS_DATA['final_id'], password='MEPHI_sucks')
                        except:
                            print(f'Unable to join user {user} to final')
                        if res['ok']:
                            event = {
                                'heading': 'Участник присоединился к Финальному турниру',
                                'content': user.get_full_name() + ' был добавлен в турнир финалистов',
                                'type': Activity.Types.PROMOTED,
                                'user': user
                            }
                            Activity.objects.create(**event)

                            print(f"User {user.email} added to final.")
                    except:
                        print(f"Failed to add user {user.email} to final.")