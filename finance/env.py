from os import environ
from typing import Final
from dotenv import dotenv_values


config = dict(dotenv_values(".env")) # Переводим окружение в словарь

class TgKeys:
    TOKEN: Final = config.get('TOKEN', 'define TOKEN!')


class PgKeys:
        NAME : Final = config.get('NAME', 'define NAME')
        USER : Final = config.get('USER', 'define USER')
        PASSWORD : Final = config.get('PASSWORD', 'define PASSWORD')
        DB_HOST  : Final = config.get('DB_HOST', 'define DB_HOST')
        PORT : Final = config.get('PORT', 'define PORT')

class DjangoKey:
    SECRET_KEY : Final = config.get('SECRET_KEY', 'define SECRET_KEY')


class TinkoffKey:
    TOKEN : Final = config.get('TOKEN_TINKOFF', 'define TOKEN_TINKOFF')
