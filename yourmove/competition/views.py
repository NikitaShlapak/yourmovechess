import os

import pkce
import requests
import berserk
import lichess
from berserk.clients import Teams

from bs4 import BeautifulSoup as bs
from django.contrib.auth import logout as django_logout, login
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy


from competition import utils
from competition.forms import *
from competition.models import *
from competition.utils import *


from yourmove.config import LICHESS_DATA, ALLOWED_HOSTS

login_form = LogInForm()


def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)


def index(request):
    return render(request, 'competition/index.html', context={'login_form': login_form})


def profile(request, user_id):
    user = CustomUser.objects.get(pk=user_id)

    state = {'state': user.get_state_display()}
    if user.state in [CustomUser.States.REJECTED, CustomUser.States.UNCONFIRMED]:
        state['color'] = 'text-danger'
    elif user.state == CustomUser.States.CONFIRMED:
        state['color'] = 'text-success'
    else:
        state['color'] = 'text-primary'
    # print(request.user.pk)
    if request.user.is_authenticated and request.user.pk == user_id:
        log = True
    else:
        log = False

    acts = Activity.objects.order_by('-date').filter(user=user)

    data = {
        'login_form': login_form,
        'name_short': user.get_short_name(),
        'name_full': user.get_full_name(),
        'user': user,
        'my_profile': request.user == user,
        'state': state,

        'acts': acts,
        # 'lichess_link': form_log_in_with_lichess_link(),
        # 'lichess_text':
    }

    # print(user.has_valid_token())
    # print(user.access_level())
    if request.user == user:
        link = ''
        text = ''

        if user.has_valid_token():
            if user.access_level() > 200:
                if user.state not in [user.States.UNCONFIRMED, user.States.REJECTED]:
                    link = redirect('join_swiss', 0).url
                    text = 'Присоединиться к турниру'
                elif user.state == user.States.CONFIRMED :
                    link = redirect('join_team').url
                    text = 'Присоединиться к клубу'
        else:
            link = form_log_in_with_lichess_link()
            text = 'Подтверждение аккаунта на lichess.org'

        data['lichess_link'], data['lichess_text'] = link, text

    if user.links:
        links = user.links.replace(', \n', '\n').replace(', ', '\n').replace(' ', '\n').replace(',', '\n').replace('\r',
                                                                                                                   '').split(
            '\n')
        data['links'] = links

    return render(request, 'competition/profile.html', context=data)


def register_long(request):
    if request.method == 'POST':
        form = FullRegisterForm(data=request.POST)
        if form.is_valid():
            user = form.cleaned_data
            # print(user['password'])
            try:
                new_user = CustomUser.objects.create(**user)
                new_user.set_password(new_user.password)
                new_user.save(update_fields=['password', ])
                # print(new_user.pk)
                if new_user.gender == CustomUser.Gender.M:
                    desc1 = Activity.ContentSample.male['reg']
                else:
                    desc1 = Activity.ContentSample.female['reg']
                if new_user.in_extra_comp:
                    desc2 = 'подана'
                else:
                    desc2 = 'не подана'
                # print(new_user.pk)
            except:
                form.add_error(None, 'Error')
            else:
                event = {
                    'heading': 'Регистрация пользователя',
                    'content': new_user.get_full_name() + desc1 + '\nЗаявка на конкурс по шахматной композиции ' + desc2 + '.\n',
                    'type': Activity.Types.OTHER,
                    'user': new_user
                }
                # print(event)
                Activity.objects.create(**event)
                login(request=request, user=new_user)
                return redirect('register_short')
    else:
        form = FullRegisterForm()
    return render(request, 'competition/register.html', context={'form': form})


def register_short(request):
    if request.method == 'POST':
        form = RegByIDForm(data=request.POST)
        if form.is_valid():
            suc, resp = update_with_rcf(form.cleaned_data['rf_id'])
            # print(resp)
            if suc:
                print(resp['last_name'] == request.user.last_name and resp['first_name'] == request.user.first_name)
                if resp['last_name'] == request.user.last_name and resp['first_name'] == request.user.first_name:
                    user = CustomUser.objects.get(email=request.user.email)
                    print(resp)
                    user.rf_id = resp['rf_id']
                    print(resp.get('rf_id'))
                    if resp.get('fide_id'):
                        user.fide_id = resp['fide_id']

                    if resp.get('rating_standart_ru'):
                        user.rating_standart_ru = resp['rating_standart_ru']

                    if resp.get('rating_rapid_ru'):
                        user.rating_rapid_ru = resp['rating_rapid_ru']

                    if resp.get('rating_blitz_ru'):
                        user.rating_blitz_ru = resp['rating_blitz_ru']

                    if resp.get('rating_standart'):
                        user.rating_standart = resp['rating_standart']

                    if resp.get('rating_rapid'):
                        user.rating_rapid = resp['rating_rapid']

                    if resp.get('rating_blitz'):
                        user.rating_blitz = resp['rating_blitz']

                    user.save()
                    return redirect('profile', user.pk)

                else:
                    form.add_error(None, 'Указан неверный id. Вы можете подтвердить только свой рейтинг!')
            else:
                RegByIDForm(data=request.POST)
                form.add_error(None, resp)
    else:
        form = RegByIDForm()
    return render(request, 'competition/short_register.html', context={'form': form, 'login_form': login_form})


class LoginUser(LoginView):
    form_class = LogInForm
    template_name = 'competition/login.html'

    def get_success_url(self):
        return reverse_lazy('main')


def logout(request):
    django_logout(request)
    return redirect('login')


def update_with_rcf(id):
    try:
        r = requests.get('https://ratings.ruchess.ru/people/' + str(id))
        # print(str(r)=='<Response [200]>', type(r))
        # print(r.head)
        if r.status_code != 200 : raise Exception
        html = bs(r.content, 'html.parser')
        items = html.select("li.list-group-item > b")
        captions = html.select("li.list-group-item > strong > span")
        name_full = str(html.select("div.page-header > h1")[0])
        strs = html.select("li.list-group-item > span")

        name_full = name_full[1 + name_full.find('>'):name_full[1:].find('<')].replace('\n', '')
        # print(name_full)
        name_arr = name_full.split(' ', maxsplit=2)
        # print(name_arr)

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


def disp_list(request):
    all_users = CustomUser.objects.filter(is_banned=False, is_active=True, not_plaing=False).order_by('pk')
    users = []
    for i in range(len(all_users)):
        users.append({
            'id': all_users[i].pk,
            'place': i + 1,
            'name': all_users[i].get_full_name(),
            'short_name': all_users[i].get_short_name(),
            'status': all_users[i].ru_status(),
            'state': all_users[i].state,
            'States': all_users[i].States,
            'lichess': all_users[i].lichess_nick
        })
    data = {
        'login_form': login_form,
        'users': users
    }
    return render(request, 'competition/list.html', context=data)


def ban(request, user_id):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        user = CustomUser.objects.get(pk=user_id)
        if request.method == 'POST':
            form = BanForm(data=request.POST)
            if form.is_valid():
                # print(form.cleaned_data)
                if form.cleaned_data['content']:
                    content = 'с комментарием:\n"' + form.cleaned_data['content'] + '"'
                    if not form.cleaned_data['hide_name']:
                        content += '\n(c) ' + request.user.get_short_name() + '.'
                else:
                    content = 'без объяснения причины.'
                    if not form.cleaned_data['hide_name']:
                        content = request.user.get_short_name() + '. ' + content
                # print(content)
                user.is_banned = True
                user.save()
                event = {
                    'heading': 'Участник дисквалифицирован',
                    'content': user.get_full_name() + ' был дисквалифицирован ' + content,
                    'type': Activity.Types.BANNED,
                    'user': user
                }
                # print(event)
                Activity.objects.create(**event)
                return redirect('main')
        else:
            form = BanForm()
        data = {
            'id': user_id,
            'form': form,
            'user': user
        }
        return render(request, 'competition/ban.html', context=data)
    else:
        return redirect('403')


def Forbidden(request):
    return render(request, 'competition/aden.html')


def confirm(request, user_id):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        user = CustomUser.objects.get(pk=user_id)
        if user.state == CustomUser.States.UNCONFIRMED:
            user.state = CustomUser.States.CONFIRMED
            user.save()
            event = {
                'heading': 'Заявка принята',
                'content': user.get_full_name() + ' был допущен к отборочным соревнованиям ' + request.user.get_short_name() + '.',
                'type': Activity.Types.PROMOTED,
                'user': user
            }
            # print(event)
            Activity.objects.create(**event)
            if user.has_valid_token():
                token = user.lichess_token
                try:
                    session = berserk.TokenSession(token)
                    client = utils.BetterTeam(session=session)

                    message = '12345' * 7
                    password = LICHESS_DATA['team_password']

                    res = client.join(LICHESS_DATA['team_id'], message=message, password=password)
                    if res['ok']:
                        master_session = berserk.TokenSession(LICHESS_DATA['master_token'])
                        joined_res = master_session.post(
                            f'https://lichess.org/api/team/{LICHESS_DATA["team_id"]}/request/{user.lichess_nick.lower()}/accept')
                        if joined_res.status_code == 200:
                            return join_swiss(request, 0)
                        return join_swiss(request, 0)
                except:
                    return HttpResponse(
                        'Ошибка добавления в клуб. Попробуйсте снова. Если проблема не исчезнет, обратитесь в техподдержку')

        return redirect('main')
    else:
        return redirect('403')


# def api_test(request):
#     # https://github.com/ZackClements/berserk
#
#     # session = berserk.TokenSession(API_TOKEN)
#     # client = berserk.Client(session=session)
#
#    return render(request, 'api_test.html', context=data)


def lichess_auth(request):
    code = request.GET['code'].replace(' ', '')
    ver = request.GET['state'].replace(' ', '')
    # print(code)
    # print(ver)
    lichess_url = os.getenv("LICHESS_HOST", "https://lichess.org")
    token_url = lichess_url + '/api/token'
    # print(token_url)

    redir_url =  ALLOWED_HOSTS[-1] + redirect('lichess_auth').url

    token_data = {
        'grant_type': "authorization_code",
        'code': code,
        'redirect_uri': redir_url,
        'code_verifier': ver,
        'client_id': "yourmovechessid",
        'client_secret': "yourmovechessid"
    }

    try:
        req = requests.post(url=token_url, data=token_data,
                            headers={'content-type': 'application/x-www-form-urlencoded'})
        # print(req.status_code)
        token = req.json()['access_token']
    except:
        return HttpResponse(
            'Ошибка получения токена. Попробуйсте снова. Если проблема не исчезнет, обратитесь в техпоодержку')

    try:
        user = request.user
        user.lichess_token = token
        session = berserk.TokenSession(token)
        client = berserk.Client(session=session)
        user.lichess_nick = client.account.get()['username']
        user.save()

        event = {
            'heading': 'Участник подтвердил аккаунт liches.org',
            'content': user.get_full_name() + ' Подтвердил свой аккаунт и статус участника отборочного этапа. ',
            'type': Activity.Types.PROMOTED,
            'user': user
        }

        Activity.objects.create(**event)

        return redirect('profile', user.pk)
    except:
        return HttpResponse(
            'Ошибка добавления записи в базу данных. Попробуйсте снова. Если проблема не исчезнет, обратитесь в '
            'техпоодержку')


def form_log_in_with_lichess_link():
    lichess_url = os.getenv("LICHESS_HOST", "https://lichess.org")
    url = lichess_url + '/oauth'

    code_verifier, code_challenge = pkce.generate_pkce_pair()

    redir_url =  ALLOWED_HOSTS[-1] + redirect('lichess_auth').url
    token_data = {'response_type': 'code',
                  'redirect_uri': redir_url,
                  'scope': 'team:write email:read challenge:read challenge:write tournament:write',
                  'code_challenge_method': 'S256',
                  'code_challenge': code_challenge,
                  'client_id': 'yourmovechessid',
                  'state': code_verifier
                  }
    req = requests.get(url=url, params=token_data)
    return req.url


def join_team(request):
    user = request.user
    token = user.lichess_token
    try:
        session = berserk.TokenSession(token)
        client = utils.BetterTeam(session=session)

        message = '12345' * 7
        password = LICHESS_DATA['team_password']

        res = client.join(LICHESS_DATA['team_id'], message=message, password=password)
        if res['ok']:
            master_session = berserk.TokenSession(LICHESS_DATA['master_token'])
            joined_res = master_session.post(f'https://lichess.org/api/team/{LICHESS_DATA["team_id"]}/request/{user.lichess_nick.lower()}/accept')
            if joined_res.status_code == 200:
                return join_swiss(request,0)
            else:
                raise Exception
    except:
        return HttpResponse(
            'Ошибка добавления в клуб. Попробуйсте снова. Если проблема не исчезнет, обратитесь в техподдержку')

    return redirect('profile', user.pk)


def join_swiss(request, swiss_num):
    user = request.user
    token = user.lichess_token
    try:
        session = berserk.TokenSession(token)
        client = utils.BetterSwiss(session=session)


        res = [client.join(swiss) for swiss in LICHESS_DATA['swiss_ids']]
        # print(res)
        if res[0]['ok'] or res[1]['ok'] or res[2]['ok'] or res[3]['ok'] :
            event = {
                'heading': 'Участник присоединился к турниру',
                'content': user.get_full_name() + ' Включился в борьбу',
                'type': Activity.Types.PROMOTED,
                'user': user
            }

            Activity.objects.create(**event)

            user.state = user.States.ACTIVE
            user.save()
    except:
        return HttpResponse(
            'Ошибка добавления в Турниры. Попробуйсте снова. Если проблема не исчезнет, обратитесь в техподдержку')
    # return HttpResponse('OK')
    return redirect('profile', user.pk)


def board(request):
    pos = [
        ['8', ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']],
        ['7', ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp']],
        ['6', ['*', '*', '*', '*', '*', '*', '*', '*']],
        ['5', ['*', '*', '*', '*', '*', '*', '*', '*']],
        ['4', ['*', '*', '*', '*', '*', '*', '*', '*']],
        ['3', ['*', '*', '*', '*', '*', '*', '*', '*']],
        ['2', ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp']],
        ['1', ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']],
        ['0', ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']],
    ]
    data = {
        'position': pos,
    }
    return render(request, 'competition/board.html', context=data)
