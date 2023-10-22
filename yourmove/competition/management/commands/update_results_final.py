import json

import requests
from django.core.management import BaseCommand

from competition.models import CustomUser
from yourmove.config import LICHESS_DATA


class Command(BaseCommand):
    help = "Recalculating places by users' results (or pk)"
    application_mode = False

    def handle(self, *args, **options):
            swiss_id = LICHESS_DATA['final_id']
            resp = requests.get(f'https://lichess.org/api/swiss/{swiss_id}/results')
            results = []
            for line in resp.text.split('\n')[:-1]:
                results.append(json.loads(s=line))

            for user_result in results:
                print(f"Looking for {user_result['username']}.")
                try:
                    user = CustomUser.objects.filter(is_banned=False, lichess_nick=user_result['username'])[0]
                except CustomUser.DoesNotExist:
                    print(f"User {user_result['username']} not found")
                except CustomUser.MultipleObjectsReturned:
                    print(f"Found more then 1 user with nick {user_result['username']}")
                else:
                    user.resf = user_result['points']
                    user.tbf = user_result['tieBreak']
                    user.state = CustomUser.States.FINAL
                    user.save()
                    print(f"User {user} updated")




