from asgiref.sync import sync_to_async

from typing import Tuple, List
import datetime as dt

from bot import misc
from bot import reports
from bot import keyboards as kb
from bot.misc.util import beautiful_numbers as bn

from bot.models.operations import get_sum_operations_by_days



@sync_to_async
def get_list_all_operations_by_period(data: str, telegram_id: int):
    group_by = 'created_at'
    type_report, type_date, date_start_str = data.split('_')[1:]
    date = map(int, date_start_str.split('-'))
    date_start, date_end = misc.get_two_date_delta(type_date, *date)
    if type_report == 'd':
        inline = kb.inline_all_oper_for_cat(f'{type_date}_{date_start_str}')
    else:
        group_by = 'category__name'
        inline = kb.main_menu

    text = reports.get_answer_with_operations(
                telegram_id, date_start, date_end, group_by
        )
    answer = {'text' : text, 'reply_markup' : inline}
    return answer

@sync_to_async
def get_list_inline_by_days(data: str, telegram_id: int):
    type_date, date_start_str = data.split('_')[1:]
    date = [int(el) for el in date_start_str.split('-')]
    date_start, date_end = misc.get_two_date_delta(type_date, *date)
    result_list = get_sum_operations_by_days(telegram_id, date_start, date_end)
    print(result_list)
    inline = kb.get_inline_button_sum_operations_by_days(result_list, *date[:-1])
    return {
        'text' : f'Операции за {misc.month_dict[date[1]]} {date[0]}',
        'reply_markup' : inline
        }
