import re
from decimal import Decimal
import datetime as dt
from typing import Tuple, List
from asgiref.sync import sync_to_async
from bot.portfolio_bot.models.currency import get_dict_currency_reduction
from bot.portfolio_bot import misc


def get_words(text: str) -> list:
    return re.findall(r'[а-яa-z]+', text)


def get_number(text: str) -> list:
    '''
    Получаем строку ищем числа
    если находим берем первую приводим к float и возвращаем
    если нету будет ошибка
    '''
    num = [n[0] for n in re.finditer(r'\d+(\.\d+)?', text)]
    return num


def beautiful_numbers(x):
    num = f'{round(x, 2):,}'.replace(',', ' ')
    if re.search(r'\d+[.]0{1,2}\b', num):
        num = num[:num.index('.')]
    elif re.search(r'\d+[.]\d0\b', num):
        num = num[:-1]
    return num


def get_date_now() -> tuple:
    now = dt.datetime.now()
    day = now.day
    month = now.month
    year = now.year
    return year, month, day


def get_date_last_month() -> int:
    '''
    Возвращаем прошлый месяц 2022 11 30
    '''
    last_month = dt.datetime.now().replace(day=1) - dt.timedelta(days=1)
    day = last_month.day
    month = last_month.month
    year = last_month.year
    return year, month, day


def date_str_to_datetime(date_str) -> dt.datetime:
    '''
    2022-12-16 to datetime(2022, 12, 16)
    '''
    year, month, day = map(int, date_str.split('-'))
    return dt.datetime(year=year, month=month, day=day, hour=1)


@sync_to_async
def stratum_async(foo, parameter):
    if type(parameter) == dict:
        return foo(**parameter)
    elif type(parameter) == tuple or type(parameter) == list:
        return foo(*parameter)
    else:
        return foo(parameter)


def get_two_date_delta(period: str = 'day',
                       start_year: int = 0,
                       start_month: int = 0,
                       start_day: int = 0):
    '''
    period = day, month, year - текущий день, месяц, год
    можно указать дату старта и период
    по дефолту возвращает сегодня
    '''

    now_year, now_month, now_day = get_date_now()

    start_year = start_year if start_year else now_year

    if period == 'day':
        start_day = start_day if start_day else now_day
        start_month = start_month if start_month else now_month
        date_start = dt.datetime(
            year=start_year, month=start_month, day=start_day)
        date_end = date_start + dt.timedelta(days=1)
    else:
        start_day = end_day = 1
        if period == 'month':
            start_month = start_month if start_month else now_month
            if start_month == 12:
                end_year, end_month = start_year + 1, 1
            else:
                end_year, end_month = start_year, start_month + 1
        else:
            start_month = end_month = 1
            end_year = start_year + 1

        date_start = dt.datetime(
            year=start_year, month=start_month, day=start_day)
        date_end = dt.datetime(year=end_year, month=end_month, day=end_day)
    return date_start, date_end


def datetime_to_str(date_start: dt.datetime, date_end: dt.datetime) -> Tuple[str, str]:
    '''
    Получаем две даты и парсим для записи в калбек кнопку
    возврат дата начала и тип (day or month or year)
    '''
    days = (date_end - date_start).days
    if days > 360:
        type_report = 'year'
    else:
        type_report = 'day' if days == 1 else 'month'

    return f'{type_report}_{date_start.year}-{date_start.month}-{date_start.day}'


def create_detail_operation_sting(operation_type, args):
    if operation_type == 'acc':
        cat, sub, cur, sm, smb, curb, date, mes = args
        if cur != curb:
            mes_summa = f'{beautiful_numbers(sm)} {cur} | {beautiful_numbers(smb)} {curb}'
        else:
            mes_summa = f'{beautiful_numbers(sm)} {cur}'
        answer = f'''{date.day} {misc.month_dict[date.month]} {date.year}г.
Сумма операции: {mes_summa}\nКатегория: {cat} | {sub.capitalize()}\nСообщение: {mes}'''

    else:
        curs, curb, sms, smb, pbc, curbas, date, mes = args
        dop = '' if pbc == sms else f'({beautiful_numbers(pbc)} {curbas})'
        answer = f'''{date.day} {misc.month_dict[date.month]} {date.year}г.
{beautiful_numbers(sms)} {curs} {dop} -> {beautiful_numbers(smb)} {curb}\nСообщение: {mes}'''

    return answer


def beautiful_account_operation(operations: list) -> str:
    # 0'id',1 'category__name', 2'currency__symbol', 3'amount', 4'created_at'
    return '\n'.join([
        f'{i+1}. {data[4].month}-{data[4].day} {data[1]}: {bn(data[3])}{data[2]}  /d_a{data[0]}'
        for i, data in enumerate(operations)
    ])


def beautiful_conversion_operation(operations: list) -> str:
    # 0'id', 1'currency_sell__symbol', 2'currency_buy__symbol', 3'amount_sell', 4'amount_buy',
    # , 5 'created_at'
    return '\n'.join([
        f'{i+1}. {data[5].month}-{data[5].day} {bn(data[3])}{data[1]} -> {bn(data[4])}{data[2]}  /d_c{data[0]}'
        for i, data in enumerate(operations)
    ])
