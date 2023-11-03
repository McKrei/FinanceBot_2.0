from datetime import datetime

import requests

from django.core.management.base import BaseCommand
from env import TgKeys


class Command(BaseCommand):
    help = 'dump db to json'


    def handle(self, *args, **kwargs):
        ...
        file_path = '/home/www/FinanceBot_2.0/finance/data.json'
        url = f'https://api.telegram.org/bot{TgKeys.TOKEN}/sendDocument'
        message_text = "Dump BD Finance Bot 2.0 от " + datetime.now().strftime("%d.%m.%Y")
        params = {
            'chat_id': 415598571,
            'caption': message_text,
        }
        with open(file_path, 'rb') as file:
            response = requests.post(url, params=params, files={'document': file})
