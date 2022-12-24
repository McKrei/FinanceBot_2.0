from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageIsTooLong
from bot.finance_bot import misc
from bot.finance_bot import keyboards as kb
from bot.finance_bot import reports

from bot.finance_bot.models.operations import delete_operation
from bot.finance_bot.models.category import save_key_for_subcategory
from bot.finance_bot.models.operations import write_operation_callback
from bot.finance_bot.models.operations import update_date_operation


async def get_reports(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    type_report, date_type, date_str = callback.data.split('_')[1:]
    date_start_tuple = map(int, date_str.split('-'))
    date_start, date_end = misc.get_two_date_delta(date_type, *date_start_tuple)
    type_report = 'category' if type_report == 'ca' else 'subcategory'
    answer = await reports.get_report_table_for_period(telegram_id,
                                                        date_start,
                                                        date_end,
                                                        type_report)

    try:
        await callback.message.answer(**answer)
        await callback.answer()
    except MessageIsTooLong:
        await misc.report_message_is_tooLong(callback, answer)



async def get_report_month_of_year(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    year = int(callback.data.split('_')[1])
    tuple_dicts_answers = await reports.get_answer_reports(telegram_id, year=year)
    await callback.message.answer(**tuple_dicts_answers[0])
    await callback.answer()


async def enter_delete_operation(callback: CallbackQuery):
    '''
    Запрос удаление операции
    '''
    type_operation, operation_id = callback.data.split('_')[1:]
    if type_operation =='conv':
        await callback.message.answer('Конверсионные операции возможно удалить только после создания')
        await callback.answer(f'Ошибка')
        return
    answer = await misc.stratum_async(delete_operation, {
        'type_operation': type_operation,
        'operation_id': int(operation_id)})
    if answer:
        await callback.message.answer(answer)
    await callback.answer(f'Операция удалена')




async def enter_update_operation(callback: CallbackQuery):
    '''
    Запрос изменение операции, выбор даты
    '''

    type_operation, operation_id, date = callback.data.split('_')[1:]
    result = await misc.stratum_async(foo=update_date_operation,
        parameter={'type_operation': type_operation,
                    'operation_id': int(operation_id),
                    'new_date': misc.date_str_to_datetime(date)})

    answer = f'Операция перезаписана\n{date}' if result else 'операции не существует'
    await callback.answer(answer)


async def get_button_for_update_operation(callback: CallbackQuery):
    '''
    Запрос изменение операции, выбор даты
    '''
    type_month, type_operation, id_operation = callback.data.split('_')[1:]
    inline = kb.inline_get_date_update_operation(type_operation, int(id_operation), type_month)
    month = 'Этот' if type_month == 'now' else 'Прошлый'
    await callback.message.answer(f'{month} месяц:', reply_markup=inline)
    await callback.answer()


async def get_visualization(callback: CallbackQuery):
    '''TODO visualization'''
    await callback.answer(callback.data)


async def get_all_operations(callback: CallbackQuery):
    '''TODO get_all_operations'''
    data = callback.data
    telegram_id = callback.from_user.id
    answer = await reports.get_list_all_operations_by_period(data, telegram_id)
    await callback.message.answer(**answer)
    await callback.answer()


async def get_reports_by_days(callback: CallbackQuery):
    '''TODO get_reports_by_days'''
    data = callback.data
    telegram_id = callback.from_user.id
    answer = await reports.get_list_inline_by_days(data, telegram_id)
    await callback.message.answer(**answer)
    await callback.answer()

async def do_operation(callback: CallbackQuery):
# csc_{osn_id}_{summa}_{cur_id}_{word}
    telegram_id = callback.from_user.id
    answers = await misc.stratum_async(
        foo=write_operation_callback,
        parameter=callback.data.split('_')[1:])
    for answer in answers:
        await callback.message.answer(**answer)
    await callback.answer()


async def get_button_subcategory(callback: CallbackQuery):
    # gdu_{cat_id}_{summa}_{cur_id}_{word}
    answers = await kb.create_inline_subcat(callback.data)
    for answer in answers:
        await callback.message.answer(**answer)
    await callback.answer()


async def write_key_subcategory(callback: CallbackQuery):
# f'sksc_{sub_id}_{word}'
    data = callback.data
    answer = await save_key_for_subcategory(data)
    await callback.answer(answer)

async def enter_currency_for_oper(callback: CallbackQuery):
# gc_{summa}_{money.currency.id}
    tg = callback.from_user.id
    data = callback.data.split('_')[1:]
    inline = await misc.stratum_async(
        foo=kb.inline_choice_categories,
        parameter=(tg, data))
    await callback.message.answer(
        f'Выберите категорию', reply_markup=inline)
    await callback.answer()



def register_callback_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(get_reports, Text(startswith='r_'))
    dp.register_callback_query_handler(get_all_operations, Text(startswith='allO_')) # allO - все операции
    dp.register_callback_query_handler(get_reports_by_days, Text(startswith='byD_')) # byD - по дням
    dp.register_callback_query_handler(get_report_month_of_year, Text(startswith='repyear_'))
    dp.register_callback_query_handler(do_operation, Text(startswith='wo_')) # write operation
    dp.register_callback_query_handler(enter_currency_for_oper, Text(startswith='gc_')) # get currency

    dp.register_callback_query_handler(enter_delete_operation, Text(startswith='do_')) # Delate operation
    dp.register_callback_query_handler(enter_update_operation, Text(startswith='ud_'))
    dp.register_callback_query_handler(get_button_for_update_operation, Text(startswith='gdu_'))
    dp.register_callback_query_handler(get_button_subcategory, Text(startswith='gsc_')) #get subcat
    dp.register_callback_query_handler(write_key_subcategory, Text(startswith='sksc_'))  # save key subcat

    dp.register_callback_query_handler(get_visualization, Text(startswith='v_')) # ВИЗУАЛИЗАЦИЯ

    pass
