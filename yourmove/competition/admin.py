from django.contrib import admin, messages
from .models import *
from django.utils.translation import gettext_lazy as _


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('place','email', 'last_name', 'first_name', 'b_date', 'region', 'SSK', 'lichess_nick', 'rf_id', "state", 'is_banned')
    list_display_links = ('email', 'last_name', "first_name")
    search_fields = ('email', 'last_name', 'first_name')
    sortable_by = ('place','email', 'last_name', 'first_name', 'b_date', 'SSK', 'lichess_nick', 'rf_id', "state", 'is_banned')
    list_filter = ('region', 'state', 'gender','in_extra_comp')
    list_editable = ("state", 'is_banned','rf_id')
    readonly_fields = ('last_login', 'place', 'lichess_token')


    fieldsets = (
        ('Учётная запись', {"fields": ("email", "password"), }),
        (_("Personal info"), {"fields": ("last_name", "first_name", "middle_name","gender","b_date","phoneNumber")}),
        ('Учебное заведение и спортивный клуб', {"fields": ("region", "city","university","SSK"),"classes": ["collapse"]}),
        ('Аккаунт lichess.org', {"fields": ("lichess_nick", "lichess_token")}),
        ('Аккаунты РШФ и FIDE', {"fields":("rf_id",
                                           "fide_id",
                                           "rating_standart_ru",
                                           "rating_rapid_ru",
                                           "rating_blitz_ru",
                                           "rating_standart",
                                           "rating_rapid",
                                           "rating_blitz",)}),
        ('Участие в проекте', {"fields": ("state", "place", "res1", "res2", "tb1", "tb2", "is_banned"),"classes": ["collapse"]}),
        ('Дополнительно', {"fields": ("in_extra_comp", "links"),"classes": ["collapse"],}),
        (
            _("Permissions"),
            {"classes": ["collapse"],
             "description":'Служебные настройки доступа. Если не знаешь, что делаешь, лучше сверни обратно!',
             "fields": (
                "not_plaing",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    actions = ['confirm_applications','reset_lichess']
    @admin.action(description='Обновить рейтинги')
    def confirm_applications(self, request, queryset):
        updated_fields = 0
        for user in queryset:
            updated = user.refresh_ratings_self()
            if updated:
                updated_fields = updated_fields + int(updated)
        if updated_fields:
            self.message_user(request,
                          f'{len(list(queryset))} пользователей было обновлено. Изменено полей: {updated_fields}.',
                          messages.SUCCESS)
        else:
            self.message_user(request,
                              f'{len(list(queryset))} пользователей было обновлено. Изменений рейтингов не потребовалось.',
                              messages.SUCCESS)

    @admin.action(description='Отвязать lichess')
    def reset_lichess(self, request, queryset):
        updated = 0
        not_updated = 0
        for user in queryset:
            try:
                user.lichess_token = ''
                user.lichess_nick = ''
                user.save()
            except:
                not_updated +=1
            else:
                updated += 1
        if updated:
            self.message_user(request,
                          f'{updated} пользователей было обновлено. Не удалось обновить: {not_updated}.',
                          messages.SUCCESS)
        else:
            self.message_user(request,
                              f' Не удалось обновить пользователей. Всего ошибок: {not_updated}',
                              messages.ERROR)



class ActivityAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'user', 'content')
    list_display_links = ('date','user')
    search_fields = ('date', 'type', 'user', 'content')

class PasswordResetModelAdmin(admin.ModelAdmin):
    list_display_links = list_display = ('user', 'created', 'code')
    search_fields = ('user__email', 'user__lichess_nick', 'user__first_name', 'user__last_name')


admin.site.register(PasswordResetModel, PasswordResetModelAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Activity, ActivityAdmin)

AUTH_USER_MODEL = 'abstract_base_user_sample.CustomUser'
