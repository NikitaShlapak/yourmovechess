from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8mb8@w8hrh-g^h+5#8@m32lu=044yx$n9#f#%@bxv_j4q#=#xm'

LICHESS_DATA = {
    'master_api_token': 'lip_c3WYH3T3whEZPEkLJJwz',
    'team_id': 'iate-chess-hampionship-----',
    'team_password': '123',
    'swiss_passwords': ('123',),
    'swiss_ids': ('P1JV3Uzd',),
}

ALLOWED_HOSTS = ['http://127.0.0.1:8000/', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}