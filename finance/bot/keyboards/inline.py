

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async



from bot.models.category import get_cat_by_tg
from bot.models.category import get_subcat_by_catid
from bot.models.category import check_for_one_sub

import datetime as dt
from bot.misc.util import beautiful_numbers as bn
from bot import misc


def inline_for_main_report_first() -> InlineKeyboardMarkup:
    year, month, day = misc.get_date_now()
    data_now = f'{year}-{month}-{day}'
    buttons_list = [
        InlineKeyboardButton('День', callback_data=f'r_ca_day_{data_now}'),
        InlineKeyboardButton('Месяц', callback_data=f'r_ca_month_{data_now}'),
        InlineKeyboardButton('Год', callback_data=f'r_ca_year_{data_now}')
    ]
    return InlineKeyboardMarkup(row_width=3).add(*buttons_list)


def inline_for_report_monthly(year: int = 0, start_month: int = 1) -> InlineKeyboardMarkup:
    year_now, month_now, _ = misc.get_date_now()
    if not year: year = year_now
    end_month = 12 if year_now != year else month_now
    buttons_list = [
        InlineKeyboardButton(
            misc.month_dict[month],
            callback_data=f'r_ca_month_{year}-{month}-1')
            for month in range(end_month, start_month -1, -1)]
    but_year = InlineKeyboardButton('За весь год', callback_data=f'r_ca_year_{year}-1-1')
    inline = InlineKeyboardMarkup(row_width=3).add(*buttons_list)
    return inline.row(but_year)


def inline_for_report_years(year_start: int, year_end: int) -> InlineKeyboardMarkup:
    year_start = year_start if year_start > 2000 else 2000
    buttons_list = [
        InlineKeyboardButton(
            year, callback_data=f'repyear_{year}')
            for year in range(year_end - 1, year_start - 1, -1)]
    return InlineKeyboardMarkup(row_width=4).add(*buttons_list)



def inline_for_operations(id_operation:int, type_operation: str) -> InlineKeyboardMarkup:
    '''
    Создаем кнопки отмена и выбор даты для обоих типов операций
    Возврат InlineKeyboardMarkup
    do_ - delete operation
    gdu - get date update
    '''
    buttons = [
        InlineKeyboardButton('Отмена', callback_data=f'do_{type_operation}_{id_operation}'),
        InlineKeyboardButton('Дата', callback_data=f'gdu_now_{type_operation}_{id_operation}')
    ]
    return InlineKeyboardMarkup(row_width=2).add(*buttons)



def inline_key_for_subcat(sub_id, word):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton(
            f'Сохранить {word}',
            callback_data=f'sksc_{sub_id}_{word}' # save key subcat
            )
    )
    pass



def inline_get_date_update_operation(type_operation:str,
            id_operation:int,
            type_month: str) -> InlineKeyboardMarkup:
    '''
    Создаем кнопки для выбора даты операции
    '''
    year_now, month_now, day_now = misc.get_date_now()
    type_month = type_month if day_now != 1 else 'last'


    if type_month == 'last':
        year, month, last_day = misc.get_date_last_month()
    else:
        year, month, last_day = year_now, month_now, day_now - 1

    buttons_list = [
        InlineKeyboardButton(text=day,
            callback_data=f'ud_{type_operation}_{id_operation}_{year}-{month}-{day}')
            for day in range(last_day, 0, -1)
    ]
    inline = InlineKeyboardMarkup(row_width=5).add(*buttons_list)
    if type_month == 'now':
        inline.row(InlineKeyboardMarkup(
            text='Прошлый месяц', callback_data=f'gdu_last_{type_operation}_{id_operation}'))
    return inline



def get_inline_button_report_period(date_start: dt.datetime,
                                    date_end: dt.datetime,
                                    cat_sum: dict,
                                    income: list,
                                    expense: list,
                                    type_report: str) -> InlineKeyboardMarkup:
    '''
    кнопки для отчета
    '''
    inline_list = []
    year = True if (date_end - date_start).days > 360 else False
    report_for = misc.datetime_to_str(date_start, date_end)
    type_rep_short = 'sc' # subcategory
    inline = InlineKeyboardMarkup(row_width=2)
    if type_report == 'category':
        type_rep_short = 'ca' # category
        inline.row(
            InlineKeyboardButton('Показать Подкатегории', callback_data=f'r_sc_{report_for}')
            )
    if report_for[0] == 'y':
        inline_list.append(
            InlineKeyboardButton('График', callback_data=f'v_gr_{type_rep_short}_{report_for}')
            )
    else:
        inline_list += [
            InlineKeyboardButton('Все операции', callback_data=f'allO_d_{report_for}'),
            InlineKeyboardButton('По дням', callback_data=f'byD_{report_for}')
        ]
    inline_list.append(
        InlineKeyboardButton('Пирожок', callback_data=f'v_cr_{type_rep_short}_{report_for}')
        )
    inline.add(*inline_list)
    return inline


def inline_all_oper_for_cat(text:str) -> InlineKeyboardButton:
    inline = InlineKeyboardMarkup().row(
            InlineKeyboardButton('По категориям', callback_data=f'allO_c_{text}')
            )
    return inline


def get_inline_button_sum_operations_by_days(
                        result_list: list,
                        year: str,
                        month: str) -> InlineKeyboardButton:
    buttons_list = [
        InlineKeyboardButton(f'{day}. {bn(summa)} {cur}', callback_data=f'allO_d_day_{year}-{month}-{day}')
        for day, summa, cur in result_list
    ]
    return InlineKeyboardMarkup(row_width=3).add(*buttons_list)



def inline_choice_subcategories(data: tuple,
                                word: str='') -> InlineKeyboardButton:
    # cat, summa_numbers, cur
    cat_id, summa, cur_id = data
    cat_name, subcat_list = get_subcat_by_catid(cat_id)
    buttons_list = []
    osn_id = 0
    for sub_id, sub_name in subcat_list:

        if sub_name == cat_name:
            osn_id = sub_id
            continue
        buttons_list.append(
            InlineKeyboardButton(
                sub_name.capitalize(),
                callback_data=f'wo_{sub_id}_{summa}_{cur_id}_{word}'
                ) # write operation
        )
    inline = InlineKeyboardMarkup(row_width=2).add(*buttons_list).row(
        InlineKeyboardButton(
            'Остальное',
                callback_data=f'wo_{osn_id}_{summa}_{cur_id}_{word}'
        )
    )
    return inline


def inline_choice_categories(telegram_id: int,
                            data: tuple,
                            word: str='') -> InlineKeyboardButton:

    summa, cur_id = data
    cat_list = get_cat_by_tg(telegram_id)

    buttons_list = [
        InlineKeyboardButton(
            f'{name.capitalize()} {"➕" if ioe else "➖"}',
        callback_data=f'gsc_{id}_{summa}_{cur_id}_{word}')
        for id, name, ioe in cat_list
    ]

    return InlineKeyboardMarkup(row_width=2).add(*buttons_list)


@sync_to_async
def create_inline_subcat(data: str):
    cat_id, summa, cur_id, word = data.split('_')[1:]

    cat_id, cur_id = map(int, (cat_id, cur_id))
    summa = float(summa)
    result, answer = check_for_one_sub(cat_id, summa, cur_id, word)
    if not result:
        inline = inline_choice_subcategories(
            (cat_id, summa, cur_id), word)

        return [{'text' : f'Сумма {bn(summa)}\nВыберете подкатегорию:',
                'reply_markup':inline
                }]
    return answer



def inline_choice_currency(data: tuple):
    summa, subcat, monies = data
    if subcat:
        buttons_list = [
            InlineKeyboardButton(
                f'{money.currency.name}',
                callback_data=f'wo_{subcat.id}_{summa}_{money.currency.id}_')
                for money in monies
        ]
    else:
        buttons_list = [
            InlineKeyboardButton(
                f'{money.currency.name}',
                callback_data=f'gc_{summa}_{money.currency.id}')
                for money in monies
        ]
    return InlineKeyboardMarkup(row_width=2).add(*buttons_list)
