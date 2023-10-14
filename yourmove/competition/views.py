import logging
import os

import pkce
import requests

from django.contrib.auth import logout as django_logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from competition.forms import *
from competition.models import *
from competition.utils.chess_utils import *
from competition.utils.text_utils import format_string

from yourmove.config import LICHESS_DATA, ALLOWED_HOSTS


login_form = LogInForm()


def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)

def index(request):
    return render(request, 'competition/index.html', context={'login_form': login_form})

@login_required()
def profile(request, user_id):
    user = CustomUser.objects.get(pk=user_id)

    state = {'state': user.get_state_display()}
    if user.state in [CustomUser.States.REJECTED, CustomUser.States.UNCONFIRMED]:
        state['color'] = 'text-danger'
    elif user.state == CustomUser.States.CONFIRMED:
        state['color'] = 'text-success'
    else:
        state['color'] = 'text-primary'
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
    }
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
            link = redirect('lichess_auth').url
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
            try:
                new_user = CustomUser.objects.create(**user)
                new_user.set_password(new_user.password)
                new_user.save(update_fields=['password'])
                if new_user.middle_name:
                    if new_user.middle_name.endswith('a'):
                        new_user.gender = CustomUser.Gender.F
                # print(new_user.pk)
                if new_user.gender == CustomUser.Gender.M:
                    desc1 = Activity.ContentSample.male['reg']
                else:
                    desc1 = Activity.ContentSample.female['reg']
                if new_user.in_extra_comp:
                    desc2 = 'подана'
                else:
                    desc2 = 'не подана'

            except:
                form.add_error(None, 'Error')
            else:
                event = {
                    'heading': 'Регистрация пользователя',
                    'content': new_user.get_full_name() + desc1 + '\nЗаявка на конкурс по шахматной композиции ' + desc2 + '.\n',
                    'type': Activity.Types.OTHER,
                    'user': new_user
                }
                Activity.objects.create(**event)
                new_user.email_user(subject=f"Регистрация на сайте yourmovechess.ru", message=f"Поздравляем с успешной регистрацией! "
                                                                                          f"Вы можете посетить свой личный кабинет: {ALLOWED_HOSTS[-1]}{new_user.get_absolute_url()} чтобы подтвердить свой рейтинг и прикрепить аккаунт на lichess.org. "
                                                                                          f"Это значительно ускорит проверку и автоматически добавит вас в клуб и турниры!")
                login(request=request, user=new_user)
                return redirect('register_short')
    else:
        form = FullRegisterForm()
    return render(request, 'competition/auth/register.html', context={'form': form})


def register_short(request):
    if request.method == 'POST':
        form = RegByIDForm(data=request.POST)
        if form.is_valid():
            suc, resp = update_with_rcf(form.cleaned_data['rf_id'])

            if suc:
                print(resp['last_name'], format_string(request.user.last_name),  resp['first_name'], format_string(request.user.first_name))
                if format_string(resp['last_name']) == format_string(request.user.last_name) and format_string(resp['first_name']) == format_string(request.user.first_name):
                    user = CustomUser.objects.get(email=request.user.email)

                    user.rf_id = resp['rf_id']

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
    return render(request, 'competition/auth/short_register.html', context={'form': form, 'login_form': login_form})


class LoginUser(LoginView):
    form_class = LogInForm
    template_name = 'competition/auth/login.html'

    def get_success_url(self):
        return reverse_lazy('main')


def logout(request):
    django_logout(request)
    return redirect('login')





class RangedListView(FormMixin,ListView):
    model = CustomUser
    template_name = 'competition/list.html'
    context_object_name = 'users'
    paginate_by = 1
    form_class = FilterListForm

    def get_success_url(self):
        return reverse_lazy('list')
    def get_queryset(self):
        def_filter = dict(is_banned=False, is_active=True, not_plaing=False)
        queryset = self.model.objects.filter(**def_filter)
        filter =  {}
        exclude = {}
        if self.request.GET:
            print(self.request.GET.keys(), bool(self.request.GET.get('search')))
            if not self.request.GET.get('search'):
                data = dict(self.request.GET)
                for field in data.keys():

                    if data[field][-1] != 'Не важно':
                        if field == 'states':
                            filter = filter | {'state':data[field][-1]}
                        elif field == 'rating':
                            print(data[field][-1], FilterListForm.RatingChoises.CONFIRMED, data[field][-1] == FilterListForm.RatingChoises.CONFIRMED)
                            if data[field][-1] == FilterListForm.RatingChoises.CONFIRMED:
                                filter = filter | {'rf_id__isnull':False}
                            else:
                                filter = filter | {'rf_id__isnull': True}
                        elif field == 'lichess_account':
                            if data[field][-1] == FilterListForm.LichessChoises.CONFIRMED:
                                filter = filter | {'lichess_token__contains': 'li'}
                            else:
                                exclude = exclude | {'lichess_token__contains': 'li'}

                queryset = queryset.filter(**filter)
                if exclude:
                    queryset = queryset.exclude(**exclude)
            else:
                texts = self.request.GET['search'].split(' ')
                cond = Q()
                for text in texts:
                    cond = cond | Q(first_name__icontains=text)
                    cond = cond | Q(last_name__icontains=text)
                    cond = cond | Q(middle_name__icontains=text)
                    cond = cond | Q(lichess_nick__icontains=text)
                queryset = self.model.objects.filter(cond)


        return queryset.order_by('place')

    def get_context_data(self, *args, **kwargs):
        new_context = dict(base_link_appendix='', login_form = login_form)
        if self.request.user.is_authenticated and (not self.request.user.is_banned):
            if self.request.user.place < 1000:
                new_context = new_context|dict(my_page= 1 + self.request.user.place//self.paginate_by)
        if self.request.GET:
            data = dict(self.request.GET)
            if data.get('page'):
                data.pop('page')
            self.initial = data
            data_list = [f"{key}={data[key]}".replace('[','').replace(']','').replace("'",'').replace(' ','+') for key in data.keys()]
            new_context['base_link_appendix']='&'.join(data_list)

        return super().get_context_data(*args, **kwargs) | new_context



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
                user.email_user(subject=f"Изменение статуса заявки", message=f"Вы были дисквалифицированы {content}")
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

@login_required()
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
                            else:
                                raise Exception
                        except:
                            return HttpResponse(
                                'Ошибка добавления в Турниры. Попробуйсте снова. Если проблема не исчезнет, обратитесь в техподдержку')
                        return redirect('profile', user.pk)
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

@login_required()
def lichess_auth(request):
    if request.GET:
        code = request.GET['code'].replace(' ', '')
        ver = request.GET['state'].replace(' ', '')
        user = request.user
        lichess_url = os.getenv("LICHESS_HOST", "https://lichess.org")
        token_url = lichess_url + '/api/token'

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
            token = req.json()['access_token']
        except:
            return HttpResponse(
                'Ошибка получения токена. Попробуйте снова. Если проблема не исчезнет, обратитесь в техподдержку')
        else:
            logging.info(f"Successfully created token. User - {request.user}. Saving...")

        try:
            user.lichess_token = token
            logging.info(f"Initiating token session...")
            session = berserk.TokenSession(token)
            client = berserk.Client(session=session)
            logging.info(f"Getting user nickname...")
            user.lichess_nick = client.account.get()['username']
            logging.info(f"Saving changes...")
            user.save()
            logging.info(f"Done!")
        except:
            return mark_safe(HttpResponse(
                f'Ошибка добавления записи в базу данных. Попробуйсте снова. Если проблема не исчезнет, обратитесь в '
                f'техпоодержку и сообщите следующие данные:<br> {user=}<br>{request=}<br> {token=}<br> {session=}<br> {client=}'))
        else:
            event = {
                'heading': 'Участник подтвердил аккаунт lichess.org',
                'content': user.get_full_name() + ' Подтвердил свой аккаунт и статус участника отборочного этапа. ',
                'type': Activity.Types.PROMOTED,
                'user': user
            }
            Activity.objects.create(**event)
            user.email_user(subject=f"Подтверждение аккаунта lichess.org", message=f"Ваш аккаунт {user.lichess_nick} был успешно подтверждён!"
                                                                                   f"Когда ваша заявка будет одобрена, вы автоматически будете добавлены в клуб и турниры.")
            return redirect('profile', user.pk)
    else:
        return redirect(requests.get(form_log_in_with_lichess_link()).url)



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
                  'state': code_verifier,
                  }
    req = requests.get(url=url, params=token_data)
    return req.url


def join_team(request):
    user = request.user
    token = user.lichess_token
    try:
        session = berserk.TokenSession(token)
        client = BetterTeam(session=session)

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
            'Ошибка добавления в клуб. Попробуйте снова. Если проблема не исчезнет, обратитесь в техподдержку')

    return redirect('profile', user.pk)


def join_swiss(request, swiss_num):
    user = request.user
    token = user.lichess_token
    try:
        session = berserk.TokenSession(token)
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
    except:
        return HttpResponse(
            'Ошибка добавления в Турниры. Попробуйсте снова. Если проблема не исчезнет, обратитесь в техподдержку')
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
