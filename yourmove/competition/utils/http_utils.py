import requests
from bs4 import BeautifulSoup as bs

from competition.utils.text_utils import format_string


def update_with_rcf(id):
    try:
        r = requests.get('https://ratings.ruchess.ru/people/' + str(id))
        if r.status_code != 200 : raise Exception
        html = bs(r.content, 'html.parser')
        items = html.select("li.list-group-item > b")
        captions = html.select("li.list-group-item > strong > span")
        name_full = str(html.select("div.page-header > h1")[0])
        strs = html.select("li.list-group-item > span")

        name_full = name_full[1 + name_full.find('>'):name_full[1:].find('<')].replace('\n', '')
        name_full = format_string(name_full)
        name_arr = name_full.split(' ', maxsplit=2)

        caps = []
        for el in captions:
            caps.append(
                el.text.replace(':', '').replace('Классические', 'rating_standart_ru').replace('Быстрые',
                                                                                               'rating_rapid_ru').replace(
                    'Блиц', 'rating_blitz_ru'))

        nums = []
        for el in items:
            nums.append(el.text)

        ratings = {caps[i]: nums[3 * i] for i in range(len(caps))}

        if len(strs):
            fide_id = html.select_one("li.list-group-item > a").text
            for el in strs:
                rt = el.text.split(':')
                rtl = ''
                if rt[0] == 'std':
                    rtl = 'rating_standart'
                elif rt[0] == 'rpd':
                    rtl = 'rating_rapid'
                elif rt[0] == 'blz':
                    rtl = 'rating_blitz'
                ratings[rtl] = rt[1]

        r_max = ['None:', 0]
        for r_type in ratings:
            if int(ratings[r_type]) > r_max[1]:
                r_max = [r_type, int(ratings[r_type])]

        data = ratings
        data['rf_id'] = id
        data['last_name'] = name_arr[0].replace(' ', '').capitalize()
        data['first_name'] = name_arr[1].replace(' ', '').capitalize()
        data['middle_name'] = name_arr[2].replace(' ', '').capitalize()
        if len(strs): data['fide_id'] = fide_id
        return True, data
    except:
        return False, 'Игрок с таким ФШР id не найден '

