from asgiref.sync import sync_to_async
from typing import List
from mainapp.models import User
from mainapp.models import Telegram


list_telegrams_id = tuple([i[0] for i in Telegram.objects.all().values_list('id')])


@sync_to_async
def tg_to_user(telegram_id: int) -> int:
    return Telegram.objects.filter(id=telegram_id)[0].user_id



@sync_to_async
def get_basic_currency(user_id: int) -> str:
    return User.objects.filter(id=user_id)[0].basic_currency.symbol
