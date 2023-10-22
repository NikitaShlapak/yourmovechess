from django.urls import path
from django.views.decorators.cache import cache_page

from .password_reset_views import PasswordResetInitialView, PasswordResetConfirmView, PasswordResetInfoView
from .views import *

urlpatterns = [
    path('', index, name='main'),
    path('profile/<int:user_id>', profile, name='profile'),
    path('registration', register_long, name='register'),
    path('fast_registration', register_short, name='register_short'),
    path('login', LoginUser.as_view(), name='login'),
    path('logout', logout, name='logout'),
    path('list', RangedListView.as_view(), name='list'),
    path('ban/<int:user_id>', ban, name='ban'),
    path('confirm/<int:user_id>', confirm, name='confirm'),
    path('403', Forbidden, name='403'),
    path('lichess_aut', lichess_auth, name='lichess_auth'),
    # path('api', api_test, name='api_test'),
    path('join_team', join_team, name='join_team'),
    path('join_swiss/<int:swiss_num>', join_swiss, name='join_swiss'),
    path('board',board, name='board'),

    path('password_reset/request', PasswordResetInitialView.as_view(), name='reset_password_init'),
    path('password_reset/confirm', PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
    path('password_reset_done/<str:action>', PasswordResetInfoView.as_view(), name='reset_password_done')

]
