from datetime import datetime


from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import FormView, TemplateView

from competition.forms import PasswordResetInitForm, PasswordResetForm
from competition.models import PasswordResetModel, CustomUser
from competition.utils.chess_utils import DataMixin

from yourmove.config import ALLOWED_HOSTS


class PasswordResetInitialView(DataMixin, FormView):
    form_class = PasswordResetInitForm
    template_name = 'competition/auth/password_reset.html'

    def get_context_data(self, **kwargs):
        kwargs['action']='init'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        data = form.data
        try:
            user = CustomUser.objects.get(email = data['email'])
        except CustomUser.DoesNotExist:
            form.add_error('email','Пользователь с таким email не найден')
            return self.render_to_response(self.get_context_data(form=form, action='init'))
        except CustomUser.MultipleObjectsReturned:
            form.add_error('email','На эту почту зарегистрировано несколько аккаунтов. Обратитесь в техподдержку')
            return self.render_to_response(self.get_context_data(form=form, action='init'))
        else:
            try:
                new_reset =  PasswordResetModel.objects.create(user = user, code = data['csrfmiddlewaretoken'])
            except:
                form.add_error(None,'Мы не смогли создать ссылку для сброса пароля. Попробуйте ещё раз позже. Если ситуация повторится - обратитесь в техподдержку.')
                return self.render_to_response(self.get_context_data(form=form, action='init'))
            else:
                link = f"{ALLOWED_HOSTS[-1]}/password_reset/confirm?user={new_reset.user.email}&code={new_reset.code}"
                user.email_user(subject=f"Ход за тобой | Сброс пароля",
                                message=f"Для вашего аккаунта был запрошен сброс пароля. Если это сделали не вы, то игнорируйте это письмо."
              f"Ссылка для сброса пароля: {link} ."
              f"Учтите, что она действительна в течение часа с момента создания!")
                return redirect('reset_password_done', 'request')





class PasswordResetConfirmView(DataMixin, FormView):
    form_class = PasswordResetForm
    template_name = 'competition/auth/password_reset.html'
    success_url = 'reset_password/done/confirm'
    def get_context_data(self, **kwargs):
        kwargs['action']='confirm'
        return super().get_context_data(**kwargs)
    def get(self,request,*args,**kwargs):
        if 'user' in request.GET.keys() and 'code' in request.GET.keys():
            user = get_object_or_404(CustomUser, email=request.GET["user"])
            reset_data = {'user':user,'code':request.GET["code"]}
            reset_object = get_object_or_404(PasswordResetModel, **reset_data)
            now = datetime.now()
            time_escaped =datetime.replace(now, tzinfo=None) - datetime.replace(reset_object.created, tzinfo=None)
            seconds_escaped = time_escaped.seconds - 3600*3
            if seconds_escaped < 3600:
                context = self.get_context_data(code=request.GET["code"])
                self.initial = {'code':request.GET["code"]}
                return self.render_to_response(context)
            else:
                raise Http404("Время действия кода истекло")
        else:
            raise Http404("Неверный адрес")

    def form_valid(self, form):
        data = form.cleaned_data
        if data['password_1'] != data['password_2']:
            form.add_error('password_2', 'Пароли должны совпадать')
            return self.render_to_response(self.get_context_data(form=form, code=form.data['code']))
        else:
            reset_object = get_object_or_404(PasswordResetModel, code=form.data['code'])
            user = reset_object.user
            user.set_password(data['password_1'])
            user.save()
            reset_object.delete()
            return redirect('reset_password_done', 'confirm')



class PasswordResetInfoView(DataMixin, TemplateView):
    template_name = 'competition/auth/password_reset.html'
    def get(self, request, *args, **kwargs):
        if kwargs['action'] == 'request':
            text = "На указанный адрес электронной почты выслана ссылка для восстановления. Перейдите по ней и создайте новый пароль."
        elif kwargs['action'] == 'confirm':
            text = mark_safe(f'Новый пароль сохранён! Теперь вы можете <a href=https://yourmovechess.ru/login>Войти</a> в аккаунт с его помощью.')
        context = self.get_context_data(**kwargs, text=text)
        return self.render_to_response(context)
