from django.core.management import BaseCommand
from django.db.models import F

from competition.models import CustomUser


class Command(BaseCommand):
    help = "Recalculating places by users' results (or pk)"
    application_mode = False
    def handle(self, *args, **options):
        users = CustomUser.objects.filter(is_banned=False, is_active=True, not_plaing=False).order_by((F('res1')+F('res2')).desc(),(F('tb1')+F('tb2')).desc(),'pk')
        for n, user in enumerate(users):
            user.place = n+1
            user.save()