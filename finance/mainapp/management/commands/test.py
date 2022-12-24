from datetime import datetime
from django.core.management.base import BaseCommand

from portfolio.models import *

class Command(BaseCommand):
    help = 'TECN'


    def handle(self, *args, **kwargs):
        # Запись активов
        # a = Asset()
        # a.get_data()


        a = Asset.objects.all()[5]
        # print(len(a))
        h = HistoryPriceAsset()
        h.validate_history(a, (2022, 11, 10))
        print(len(HistoryPriceAsset.objects.all()))
