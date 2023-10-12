from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import *
from django.core.validators import RegexValidator

IDRegex = RegexValidator(regex=r"^\d{1,10}$")


class RegByIDForm(forms.Form):
    rf_id = forms.RegexField(regex=r"^\d{1,10}$")

    def __init__(self, *args, **kwargs):
        super(RegByIDForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class LogInForm(AuthenticationForm):
    username = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', max_length=50, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LogInForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class FullRegisterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        req = 'Это поле является обязательным для заполнения'
        super().__init__(*args, **kwargs)
        # self.fields['region'].empty_value = 1
        self.fields['middle_name'].required = False
        self.fields['links'].required = False
        self.fields['in_extra_comp'].required = False
        self.fields['email'].error_messages = {
            'required': req,
            'invalid': "Введите корректный адрес электронной почты"
        }
        # print("\n-------------------------\n", self.fields, "\n-------------------------\n")
        for visible in self.visible_fields():
            if type(visible.field) == forms.fields.BooleanField:
                # print('\n\n\n\n\nHERE!!!\n\n\n\n')
                visible.field.widget.attrs['class'] = 'form-check-input'
            else:
                visible.field.widget.attrs['class'] = 'form-control'
            # print(type(visible.field))

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'last_name', 'first_name', 'middle_name', 'b_date', 'phoneNumber',
                  'region', 'city', 'university', 'SSK', 'lichess_nick', 'in_extra_comp', 'links']
        widgets = {
            'links': forms.Textarea(attrs={'rows': 3}),
            'university': forms.Textarea(attrs={'rows': 2}),
            'password': forms.PasswordInput(),
            'in_extra_comp': forms.CheckboxInput(attrs={'class': "form-check-input"})

        }

class BanForm(forms.Form):
    content = forms.CharField(label='Комментарий',
                              widget=forms.Textarea(
                                  attrs={'rows': 3,
                                         'class': 'form-control'}
                              ),
                              required=False)
    hide_name = forms.BooleanField(label='Скрыть моё имя',
                                   widget=forms.CheckboxInput(
                                       attrs={
                                           'class': 'form-check-input'}
                                   ),
                                   required=False)

class FilterListForm(forms.Form):
    class StateChoises(models.TextChoices):
        ANY = 'Не важно', 'Не важно'
        REJECTED = 'Отклонено', 'Заявка отклонена'                                  #50
        UNCONFIRMED = 'На проверке', 'Проверка не окончена'                         #150

        CONFIRMED = 'Проверка пройдена', 'Участник допущен к отборочному этапу'     #250

        ACTIVE = 'Отборочный этап', 'Участник принимает участие в отборочных турнирах'                      #350
        PASSED =  'Отборочный этап (Завершён)','Участник принял участие в отборочных турнирах'

        FINAL_ACCEED = 'Финал', 'Участник допущен к финалу'                      #750
        FINAL = 'Финал (завершён)', 'Участник завершил фмнальный этап'                    #850

        SUPERFINAL = 'Суперфинал', 'Участник приглашён на очный суперфинал'         #950
    class RatingChoises(models.TextChoices):
        ANY = 'Не важно', 'Не важно'
        CONFIRMED = 'Рейтинг подтверждён', 'Рейтинг подтверждён'
        UNCONFIRMED = 'Рейтинг не подтверждён','Рейтинг не подтверждён'

    class LichessChoises(models.TextChoices):
        ANY = 'Не важно', 'Не важно'
        CONFIRMED = 'Аккаунт прикреплён','Аккаунт прикреплён'
        UNCONFIRMED = 'Аккаунт не прикреплён','Аккаунт не прикреплён'

    states = forms.ChoiceField(choices=StateChoises.choices, label='Статус')
    rating = forms.ChoiceField(choices=RatingChoises.choices, label='Рейтинг')
    lichess_account = forms.ChoiceField(choices=LichessChoises.choices, label='Аккаунт')

class PasswordResetInitForm(forms.Form):
    email = forms.EmailField(label='Почта', help_text='На этот адрес будет выслана ссылка для смены пароля.')

class PasswordResetForm(forms.Form):
    password_1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput())
    password_2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput())



