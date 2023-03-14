import berserk
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.urls import reverse

from competition.hashers import *


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, first_name, last_name, password, **extra_fields):
        """
        Create and save a user with the given username, email,
        full_name, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        if not first_name:
            raise ValueError('The given first_name must be set')
        if not last_name:
            raise ValueError('The given last_name must be set')
        email = self.normalize_email(email)

        user = self.model(
            email=email, first_name=first_name, last_name=last_name,
            **extra_fields
        )
        user.set_password(PBKDF2WrappedSHA1PasswordHasher.encode(password))
        user.save(using=self._db)
        return user

    def create_user(self, email, username, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(
            email, username, full_name, password, **extra_fields
        )

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(
            email, first_name, last_name, password, **extra_fields
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Почта',
                              error_messages={'unique': "Пользователь с таким адресом электронной почты уже "
                                                        "зарегистрирован"})

    b_date = models.DateField(verbose_name='Дата рождения')

    first_name = models.CharField(max_length=20, verbose_name='Имя', null=False)
    last_name = models.CharField(max_length=20, verbose_name='Фамилия', null=False)
    middle_name = models.CharField(max_length=20, verbose_name='Отчество', null=True, blank=True)

    regions = [
        ('ЦФО', 'Центральный федеральный округ'),
        ('СЗФО', 'Северо - Западный федеральный округ'),
        ('ЮФО', 'Южный федеральный округ'),
        ('СКФО', 'Северо - Кавказский федеральный округ'),
        ('ПФО', 'Приволжский федеральный округ'),
        ('УФО', 'Уральский федеральный округ'),
        ('СФО', 'Сибирский федеральный округ'),
        ('ДФО', 'Дальневосточный федеральный округ'),
    ]

    region = models.TextField(choices=regions, verbose_name='Федеральный округ')

    phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    phoneNumber = models.CharField(validators=[phoneNumberRegex], max_length=16,
                                   verbose_name='Номер телефона', error_messages={
            'unique': "Пользователь с таким номером телефона уже зарегистрирован"})
    IDRegex = RegexValidator(regex=r"^\d{,10}$")
    rf_id = models.CharField(max_length=6, verbose_name='ФШР id', validators=[IDRegex], null=True, blank=True)
    fide_id = models.CharField(max_length=20, verbose_name='FIDE id', validators=[IDRegex], null=True, blank=True)

    ratingNumberRegex = RegexValidator(regex=r"^\d{,4}$")

    rating_standart_ru = models.CharField(validators=[ratingNumberRegex], max_length=4,
                                          verbose_name='Рейтинг ФШР (классика)', default=1000)
    rating_rapid_ru = models.CharField(validators=[ratingNumberRegex], max_length=4,
                                       verbose_name='Рейтинг ФШР (рапид)', default=1000)
    rating_blitz_ru = models.CharField(validators=[ratingNumberRegex], max_length=4,
                                       verbose_name='Рейтинг ФШР (блиц)', default=1000)
    rating_standart = models.CharField(validators=[ratingNumberRegex], max_length=4,
                                       verbose_name='Рейтинг FIDE (классика)', default=1000)
    rating_rapid = models.CharField(validators=[ratingNumberRegex], max_length=4,
                                    verbose_name='Рейтинг FIDE (рапид)', default=1000)
    rating_blitz = models.CharField(validators=[ratingNumberRegex], max_length=4,
                                    verbose_name='Рейтинг FIDE (блиц)', default=1000)

    city = models.CharField(max_length=30, verbose_name='Город, область')
    SSK = models.CharField(max_length=30, verbose_name='Название ССК')
    university = models.TextField(verbose_name='Название учебного заведения')
    lichess_nick = models.CharField(max_length=20,
                                    verbose_name='Ник на lichess.org')  # https://lichess.org/@/NikitaShlapak
    lichess_token = models.CharField(max_length=512, blank=True, default='')

    class States(models.TextChoices):
        REJECTED = 'Отклонено', 'Заявка отклонена'                                  #50
        UNCONFIRMED = 'На проверке', 'Проверка не окончена'                         #150

        CONFIRMED = 'Проверка пройдена', 'Участник допущен к отборочному этапу'     #250

        STAGE1_ACCEED = 'Этап 1', 'Участник допущен к этапу 1'                      #350
        STAGE1 = 'Этап 1 (завершён)', 'Участник завершил этап 1'                    #450

        STAGE2_ACCEED = 'Этап 2', 'Участник допущен к этапу 2'                      #550
        STAGE2 = 'Этап 2 (завершён)', 'Участник завершил этап 2'                    #650

        STAGE3_ACCEED = 'Этап 3', 'Участник допущен к этапу 3'                      #750
        STAGE3 = 'Этап 3 (завершён)', 'Участник завершил этап 3'                    #850

        SUPERFINAL = 'Суперфинал', 'Участник приглашён на очный суперфинал'         #950

    state = models.TextField(choices=States.choices, verbose_name='Статус участника', default=States.UNCONFIRMED)

    class Gender(models.TextChoices):
        M = 'Male', 'Мужской'
        F = 'Female', 'Женский'

    gender = models.TextField(choices=Gender.choices, verbose_name='Пол', default=Gender.M)

    in_streamer_comp = models.BooleanField(default=False, verbose_name='Хочу участвовать в конкурсе стримеров')

    links = models.TextField(verbose_name='Дополнительные ссылки (на профиль в соц. сетях, канал на twitch и т.п.)',
                             blank=True)

    is_banned = models.BooleanField(default=False, verbose_name='Участник дисквалифицирован')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['first_name', 'last_name']
    USERNAME_FIELD = 'email'

    objects = UserManager()

    def access_level(self):
        state = self.state

        for i in range(len(self.States)):
            if self.States.choices[i][0] == state:
                break
            i += 1
        if self.is_banned:
            ans = -100
        else:
            ans = i * 100 +50
        return ans

    def has_valid_token(self):
        try:
            session = berserk.TokenSession(self.lichess_token)
            client = berserk.Client(session=session)
            client.account.get()['username']
        except:
            return False
        return True

    def get_short_name(self):
        return self.last_name.capitalize() + ' ' + self.first_name[0].upper()

    def get_full_name(self):
        if self.middle_name:
            full_name = self.last_name.capitalize() + ' ' + self.first_name.capitalize() + ' ' + self.middle_name.capitalize()
        else:
            full_name = self.last_name.capitalize() + ' ' + self.first_name.capitalize()
        return full_name

    def ru_status(self):
        if self.state == self.States.UNCONFIRMED:
            resp = 'На расмотрении'
        elif self.state == self.States.REJECTED:
            resp = 'Заявка отклонена'
        elif self.state == self.States.CONFIRMED:
            resp = 'Заявка принята'
        elif self.state == self.States.STAGE1:
            if self.gender == self.Gender.M:
                resp = 'Отобран в полуфинал'
            else:
                resp = 'Отобрана в полуфинал'
        elif self.state == self.States.STAGE2:
            if self.gender == self.Gender.M:
                resp = 'Отобран в финал'
            else:
                resp = 'Отобрана в финал'
        elif self.state == self.States.SUPERFINAL:
            if self.gender == self.Gender.M:
                resp = 'Отобран в суперфинал'
            else:
                resp = 'Отобрана в суперфинал'
        elif self.is_banned:
            if self.gender == self.Gender.M:
                resp = 'Дисквалифицирован'
            else:
                resp = 'Дисквалифицирована'
        else:
            resp = 'ЫЫЫЫЫЫЫЫЫЫ'
        return resp

    def __str__(self):
        return self.email

    # def set_password(self, raw_password):
    #     return PBKDF2WrappedSHA1PasswordHasher.encode(raw_password)

    def get_absolute_url(self):
        return reverse('profile', kwargs={'user_id': self.pk})

    def get_max_rating(self):
        return max(self.rating_standart_ru, self.rating_rapid_ru, self.rating_blitz_ru,
                   self.rating_standart, self.rating_rapid, self.rating_blitz)

    def is_unrated(self):
        if any((self.rating_standart_ru, self.rating_rapid_ru, self.rating_blitz_ru,
                self.rating_standart, self.rating_rapid, self.rating_blitz)):
            return False
        else:
            return True

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Activity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    heading = models.CharField(max_length=200, verbose_name='Название', blank=True)
    content = models.TextField(verbose_name='Содержание')

    class ContentSample:
        male = {
            'reg': ' зарегистрировался на сайте. Добро пожаловать!'
        }
        female = {
            'reg': ' зарегистрировался на сайте. Добро пожаловать!'
        }

    date = models.DateTimeField(auto_now_add=True)

    class Types(models.TextChoices):
        REJECTED = 'Rejected', 'Заявка отклонена'
        BANNED = 'Banned', 'Участник дисквалифицирован'
        STAGE_FINISHED = 'Stage finished', 'Участник закончил отборочный этап'
        PROMOTED = 'Promoted', 'Участник переведён в следующий этап'
        OTHER = 'Other', 'Другое'

    type = models.TextField(choices=Types.choices, verbose_name='Тип события')

    def __str__(self):
        return str(self.date) + ' ' + self.user.email + ' ' + self.type

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
        ordering = ['date']
