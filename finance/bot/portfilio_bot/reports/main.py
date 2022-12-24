from prettytable import PrettyTable
from aiogram.types import Message
from aiogram.types import ParseMode
from asgiref.sync import sync_to_async

from typing import Tuple, List
import datetime as dt

from bot.portfolio_bot import misc
from bot.portfolio_bot import keyboards as kb
from bot.portfolio_bot.misc.util import beautiful_numbers as bn

from bot.portfolio_bot.models.operations import get_date_first_operation
from bot.portfolio_bot.models.operations import get_conversion_operation
from bot.portfolio_bot.models.operations import get_account_operation
from bot.portfolio_bot.models.operations import get_summa_operation
from bot.portfolio_bot.models.operations import get_sum_for_cat
from bot.portfolio_bot.models.category import get_list_cat_and_subcat


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


def create_table_category(cat_sum: dict, income: list, expense: list) -> str:
    table_expense = PrettyTable()
    sum_expense = sum_income = 0
    table_expense.field_names = ['Кат-ия', 'Расходы', 'Ост.']
    for cat in expense:
        sum_cat = cat_sum.get(cat, 0)
        sum_expense += sum_cat
        table_expense.add_row([cat.capitalize(), bn(sum_cat), bn(0)])
    table_expense.add_row(['Сумма', bn(sum_expense), bn(0)])

    table_income = PrettyTable()
    table_income.field_names = ['Категория', 'Доход']
    for cat in income:
        sum_cat = cat_sum.get(cat, 0)
        sum_income += sum_cat
        table_income.add_row([cat.capitalize(), bn(sum_cat)])
    table_income.add_row(['Сумма', bn(sum_income)])

    return f'<pre>{table_expense}\n{table_income}</pre>'


def create_table_subcategory(cat_sum: dict, income: list, expense: list) -> str:
    def create_table(cat_sum, cat_list, name) -> PrettyTable:
        table = PrettyTable()
        table.field_names = ['Категория', name]
        for cat, sub_list in cat_list:
            rows = []
            sum_cat = 0
            for sub in sub_list:
                sum_subcat = cat_sum.get(sub, 0)
                sum_cat += sum_subcat
                if sum_subcat:
                    sub_name = 'Остальное' if cat == sub else sub.capitalize()
                    rows.append([sub_name, bn(sum_subcat)])
            if sum_cat:
                table.add_row([f'+{"-"*8}+', f'+{"-"*6}+'])
                table.add_row([cat.capitalize(), bn(sum_cat)])

                if len(rows) > 1 or rows[0][0] != 'Остальное':
                    table.add_rows(rows)
        return table

    table_income = create_table(cat_sum, income, 'Доходы')
    table_expense = create_table(cat_sum, expense, 'Расходы')

    return f'<pre>{table_expense}\n{table_income}</pre>'


def get_summary_table(sum_income, sum_expense, sum_income_limit=0):
    table = PrettyTable()
    table.field_names = ['Доходы', bn(sum_income)]
    table.add_row(['Расходы', 'Лимиты'])
    table.add_row([bn(sum_expense), bn(sum_income_limit)])
    return table


def get_monthly_summary_table(telegram_id):
    date_start, date_end = misc.get_two_date_delta('month')
    income, expense = get_summa_operation(telegram_id, date_start, date_end)
    table = get_summary_table(income, expense)
    return table


# def create_str_concession()


def get_answer_with_operations(telegram_id,
                               date_start: dt.datetime,
                               date_end: dt.datetime,
                               order_by: str = 'created_at') -> str:

    account = get_account_operation(telegram_id, date_start, date_end)
    conversions = get_conversion_operation(telegram_id, date_start, date_end)
    if account or conversions:
        answer_mes = ''
        if account:
            income = account.filter(
                category__income_or_expense=True
            ).order_by(order_by).values_list('id', 'category__name', 'currency__symbol', 'price_basic_currency', 'created_at')
            expense = account.filter(
                category__income_or_expense=False
            ).order_by(order_by).values_list('id', 'category__name', 'user__basic_currency__symbol', 'price_basic_currency', 'created_at')
            if expense:
                answer_mes += 'Расходы:\n' + \
                    beautiful_account_operation(expense) + '\n'
            if income:
                answer_mes += 'Доходы:\n' + \
                    beautiful_account_operation(income) + '\n'
        if conversions:
            conv = conversions.order_by('created_at').values_list(
                'id', 'currency_sell__symbol', 'currency_buy__symbol', 'amount_sell',
                'amount_buy', 'created_at')
            answer_mes += 'Конверсионные операции:\n' + \
                beautiful_conversion_operation(conv)
        return answer_mes
    else:
        return 'Нет операций'


@sync_to_async
def get_answer_reports(telegram_id: int, year=0) -> List[dict]:
    '''
    Формируем ответ по запросу из меню отчеты.
    Ответ в формате словаря для функции answer
    '''
    year_now, month_now, day_now = misc.get_date_now()
    year = year_now if not year else year
    try:
        date = get_date_first_operation(telegram_id)
    except IndexError:
        return [{'text': 'Нет операций'}]

    data_one = {'year': year}
    if year_now == date.year:
        data_one.update({'start_month': date.month})
    result = [{
        'text': f'Подготовить отчет за {year} год:',
        'reply_markup': kb.inline_for_report_monthly(**data_one)
    }]
    if year == year_now:
        date_start, date_end = misc.get_two_date_delta()
        operations = get_answer_with_operations(
            telegram_id, date_start, date_end)
        table = get_monthly_summary_table(telegram_id)
        report_now = [{
            'text': f'{operations}\n<pre>{table}</pre>',
            'parse_mode': ParseMode.HTML,
            'reply_markup': kb.main_menu
        }]
        result = report_now + result
    if year_now == date.year or year != year_now:
        return result

    result.append({
        'text': 'Отчет за год: ',
        'reply_markup': kb.inline_for_report_years(date.year, year_now)
    })
    return result


@sync_to_async
def get_answer_reports_certain_year(telegram_id: int, year: int) -> Tuple[dict]:

    return {
        'text': 'Период подготовить отчет за: ',
        'reply_markup': kb.inline_for_report_years(date.year, year_now)
    }


@sync_to_async
def get_answer_reports_other_year(telegram_id: int) -> dict:
    try:
        start_year = first_operation_year(telegram_id)
    except IndexError:
        return False, 'Нет операций'
    # inline =


@sync_to_async
def get_report_table_for_period(telegram_id: int,
                                date_start: dt.datetime,
                                date_end: dt.datetime,
                                type_report: str = 'category') -> dict:
    '''
    Получаем период в формате строки 2-х дат от и до 2022-11-1
    Возвращаем ответ в формате словаря
    type_report: cat - только категории
                 subcat - категории и субкатегории
    '''
    cat_sum = dict(get_sum_for_cat(
        telegram_id, date_start, date_end, type_report
    ))

    if not cat_sum:
        return {
            'text': f'За данный период нет операций',
            'reply_markup': kb.main_menu
        }
    income, expense = get_list_cat_and_subcat(telegram_id, type_report)
    if type_report == 'category':
        table = create_table_category(cat_sum, income, expense)
    else:
        table = create_table_subcategory(cat_sum, income, expense)

    inline = kb.get_inline_button_report_period(date_start, date_end,
                                                cat_sum, income, expense, type_report)

    return {
        'text': table,
        'parse_mode': ParseMode.HTML,
        'reply_markup': inline
    }
