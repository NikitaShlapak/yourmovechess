import json

import requests
from django.core.management import BaseCommand
from django.db.models import F

from competition.models import CustomUser
from yourmove.config import LICHESS_DATA


class Command(BaseCommand):
    help = "Recalculating places by users' results (or pk)"
    application_mode = False

    def handle(self, *args, **options):
        for n, swiss_id in enumerate(LICHESS_DATA['swiss_ids']):
            resp = requests.get(f'https://lichess.org/api/swiss/{swiss_id}/results')
            results = []
            for line in resp.text.split('\n')[:-1]:
                results.append(json.loads(s=line))

            for user_result in results:
                try:
                    user = CustomUser.objects.get(is_banned=False, state = CustomUser.States.ACTIVE, lichess_nick=user_result['username'])
                except CustomUser.DoesNotExist:
                    print(f"User {user_result['username']} not found")
                else:
                    # print(user,user_result)
                    if not n//2:
                        if user.res1 < user_result['points']:
                            user.res1 = user_result['points']
                            user.tb1 = user_result['tieBreak']
                        elif user.res1 == user_result['points']:
                            if user.tb1 < user_result['tieBreak']:
                                user.tb1 = user_result['tieBreak']
                    else:
                        if user.res2 < user_result['points']:
                            user.res2 = user_result['points']
                            user.tb2 = user_result['tieBreak']
                        elif user.res2 == user_result['points']:
                            if user.tb2 < user_result['tieBreak']:
                                user.tb2 = user_result['tieBreak']
                    user.save()
                    print(f"User {user} updated")




