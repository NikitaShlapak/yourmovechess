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
        self.fields['in_streamer_comp'].required = False
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
                  'region', 'city', 'university', 'SSK', 'lichess_nick', 'in_streamer_comp', 'links']
        widgets = {
            'links': forms.Textarea(attrs={'rows': 3}),
            'university': forms.Textarea(attrs={'rows': 2}),
            'password': forms.PasswordInput(),
            'in_streamer_comp': forms.CheckboxInput(attrs={'class': "form-check-input"})

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
