from django.contrib import admin
from .models import *


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'last_name', 'first_name', 'b_date', 'region', 'SSK', 'lichess_nick', 'in_streamer_comp',
                    "state", 'is_banned')
    list_display_links = ('email', 'last_name', "first_name")
    search_fields = ('email', 'last_name', 'first_name', 'SSK', "lichess_nick")
    list_editable = ("state", 'is_banned')


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'user', 'content')
    list_display_links = ('date','user')
    search_fields = ('date', 'type', 'user', 'content')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Activity, ActivityAdmin)

AUTH_USER_MODEL = 'abstract_base_user_sample.CustomUser'
