from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='main'),
    path('profile/<int:user_id>', profile, name='profile'),
    path('registration', register_long, name='register'),
    path('fast_registration', register_short, name='register_short'),
    path('login', LoginUser.as_view(), name='login'),
    path('logout', logout, name='logout'),
    path('list', disp_list, name='list'),
    path('ban/<int:user_id>', ban, name='ban'),
    path('confirm/<int:user_id>', confirm, name='confirm'),
    path('403', Forbidden, name='403'),
    path('lichess_aut', lichess_auth, name='lichess_auth'),
    # path('api', api_test, name='api_test'),
    path('join_team', join_team, name='join_team'),
    path('join_swiss/<int:swiss_num>', join_swiss, name='join_swiss'),
    path('board',board, name='board')

]
