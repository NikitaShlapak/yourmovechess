import berserk
from django.contrib.auth.base_user import BaseUserManager
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils.safestring import mark_safe

from competition.hashers import PBKDF2WrappedSHA1PasswordHasher
from competition.utils.http_utils import update_with_rcf


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
        Wrapper = PBKDF2WrappedSHA1PasswordHasher()
        user.set_password(password)
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
    not_plaing = models.BooleanField(default=False)
    email = models.EmailField(unique=True, verbose_name='Почта',
                              error_messages={'unique': "Пользователь с таким адресом электронной почты уже "
                                                        "зарегистрирован"})

    b_date = models.DateField(verbose_name='Дата рождения', null=True)

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

    region = models.TextField(choices=regions, verbose_name='Федеральный округ', null=True)

    phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    phoneNumber = models.CharField(validators=[phoneNumberRegex], max_length=16,null=True,
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

    city = models.CharField(max_length=30, verbose_name='Город, область', null=True)
    SSK = models.CharField(max_length=30, verbose_name='Название ССК', null=True)
    university = models.TextField(verbose_name='Название учебного заведения',null=True)
    lichess_nick = models.CharField(max_length=20,null=True,
                                    verbose_name='Ник на lichess.org')  # https://lichess.org/@/NikitaShlapak
    lichess_token = models.CharField(max_length=512, blank=True, default='')

    class States(models.TextChoices):
        REJECTED = 'Отклонено', 'Заявка отклонена'                                  #50
        UNCONFIRMED = 'На проверке', 'Проверка не окончена'                         #150

        CONFIRMED = 'Проверка пройдена', 'Участник допущен к отборочному этапу'     #250

        ACTIVE = 'Отборочный этап', 'Участник принимает участие в отборочных турнирах'                      #350
        PASSED =  'Отборочный этап (Завершён)','Участник принял участие в отборочных турнирах'

        FINAL_ACCEED = 'Финал', 'Участник допущен к финалу'                      #750
        FINAL = 'Финал (завершён)', 'Участник завершил финальный этап'                    #850

        SUPERFINAL = 'Суперфинал', 'Участник приглашён на очный суперфинал'         #950

    state = models.TextField(choices=States.choices, verbose_name='Статус участника', default=States.UNCONFIRMED)

    class Gender(models.TextChoices):
        M = 'Male', 'Мужской'
        F = 'Female', 'Женский'

    gender = models.TextField(choices=Gender.choices, verbose_name='Пол', default=Gender.M)
    place = models.IntegerField(default=1000, verbose_name="Место", help_text="Текущее место участника в общих списках")
    res1 = models.FloatField(default=0, verbose_name="Результат первого этапа")
    res2 = models.FloatField(default=0, verbose_name="Результат второго этапа")
    tb1 = models.FloatField(default=0, verbose_name="Бухгольц первого этапа")
    tb2 = models.FloatField(default=0, verbose_name="Бухгольц второго этапа")

    in_extra_comp = models.BooleanField(default=False, verbose_name='Хочу участвовать в конкурсе по шахматной композиции')

    links = models.TextField(verbose_name='Дополнительные ссылки (на профиль в соц. сетях, канал на twitch и т.п.)',
                             blank=True, null=True)

    is_banned = models.BooleanField(default=False, verbose_name='Участник дисквалифицирован')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['first_name', 'last_name']
    USERNAME_FIELD = 'email'

    objects = UserManager()



    def refresh_ratings_self(self):
        if self.rf_id and int(self.rf_id) > 1:
            updated, resp = update_with_rcf(self.rf_id)
            if updated:
                n_fields = 0
                if resp.get('fide_id') and self.fide_id != resp['fide_id']:
                    self.fide_id = resp['fide_id']
                    n_fields += 1

                if resp.get('rating_standart_ru'):
                    self.rating_standart_ru = resp['rating_standart_ru']
                    n_fields += 1

                if resp.get('rating_rapid_ru'):
                    self.rating_rapid_ru = resp['rating_rapid_ru']
                    n_fields += 1

                if resp.get('rating_blitz_ru'):
                    self.rating_blitz_ru = resp['rating_blitz_ru']
                    n_fields += 1

                if resp.get('rating_standart'):
                    self.rating_standart = resp['rating_standart']
                    n_fields += 1

                if resp.get('rating_rapid'):
                    self.rating_rapid = resp['rating_rapid']
                    n_fields += 1

                if resp.get('rating_blitz'):
                    self.rating_blitz = resp['rating_blitz']
                    n_fields += 1

                try:
                    self.save(update_fields=resp.keys())
                except:
                    return 0
                else:
                    return n_fields
            else:
                return 0

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

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
        elif self.state == self.States.ACTIVE:
            resp = 'Принимает участие в отборочных турнирах'
        elif self.state == self.States.PASSED:
            if self.gender == self.Gender.M:
                resp = 'Принял участие в отборочных турнирах'
            else:
                resp = 'Принял участие в отборочных турнирах'
        elif self.state == self.States.FINAL_ACCEED:
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
        return int(max(self.rating_standart_ru, self.rating_rapid_ru, self.rating_blitz_ru,
                   self.rating_standart, self.rating_rapid, self.rating_blitz))

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

class PasswordResetModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания',
                                   help_text='Ссылка действительна в течение одного часа с момента создания.')
    code = models.TextField(verbose_name='Код сброса пароля')

    def __str__(self):
        return f"Объект сброса пароля пользователя {self.user} (создан {self.created.date()} в {self.created.time()})"