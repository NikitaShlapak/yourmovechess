from typing import Any

from django.core.management import BaseCommand
from pandas import DataFrame, read_csv, concat

from competition.models import CustomUser
from competition.utils.chess_utils import update_with_rcf


class Command(BaseCommand):
    help = "Updating gender of all users by the last letter of middle name"
    application_mode = False



    def read_data(self, url):
        data: DataFrame | Any = read_csv(url, sep=';',
                           names=('ID', 'full_name', 'null1', 'region', 'rating', 'null2', 'b_year', 'gender'),
                           encoding='cp1251').drop(['null1', 'null2'], axis=1)
        data['gender'] = data['gender'].fillna('m')
        data['rating'] = data['rating'].fillna(1000)
        return data
    def handle(self, *args, **options):
        print('Reading standard data...')
        df_st = self.read_data('https://ratings.ruchess.ru/api/smaster_standard.csv')
        print('Reading rapid data...')
        df_rp = self.read_data('https://ratings.ruchess.ru/api/smaster_rapid.csv')
        print('Reading blitz data...')
        df_bl = self.read_data('https://ratings.ruchess.ru/api/smaster_blitz.csv')
        print('getting unrated users from DB...')
        users = CustomUser.objects.filter(is_banned=False, is_active=True, not_plaing=False, rf_id__isnull=True)
        for user in users:
            name_long = f"{user.last_name} {user.first_name} {user.middle_name}".strip()
            name_short = user.last_name + ' ' + user.first_name

            st2 = df_st.loc[df_st['full_name'] == name_short]
            rp2 = df_rp.loc[df_rp['full_name'] == name_short]
            bl2 = df_bl.loc[df_bl['full_name'] == name_short]

            resp = concat([st2, rp2, bl2], axis=1)

            if user.middle_name:
                st1 = df_st.loc[df_st['full_name'] == name_long]
                rp1 = df_rp.loc[df_rp['full_name'] == name_long]
                bl1 = df_bl.loc[df_bl['full_name'] == name_long]
                if not resp.empty:
                    resp = concat([resp, st1, rp1, bl1], axis=1)
                else:
                    resp = concat([st1, rp1, bl1], axis=1)
            # print(resp.empty)
            if resp.empty:
                print(f"User {user.email} not found and updated")
                user.rf_id=1
                user.save()
            else:
                resp_id = resp['ID'].values[0]
                id = int(list(set(resp_id.tolist()))[-1])
                found,  rcf_data = update_with_rcf(id)
                user.rf_id = int(rcf_data['rf_id'])

                if rcf_data.get('fide_id'):
                    user.fide_id = int(rcf_data['fide_id'])

                if rcf_data.get('rating_standart_ru'):
                    user.rating_standart_ru = int(rcf_data['rating_standart_ru'])

                if rcf_data.get('rating_rapid_ru'):
                    user.rating_rapid_ru = int(rcf_data['rating_rapid_ru'])

                if rcf_data.get('rating_blitz_ru'):
                    user.rating_blitz_ru = int(rcf_data['rating_blitz_ru'])

                if rcf_data.get('rating_standart'):
                    user.rating_standart = int(rcf_data['rating_standart'])

                if rcf_data.get('rating_rapid'):
                    user.rating_rapid = int(rcf_data['rating_rapid'])

                if rcf_data.get('rating_blitz'):
                    user.rating_blitz = int(rcf_data['rating_blitz'])

                user.save()
                print(f"User {user.email} ({id=}) found and updated")
