from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters import Text

from bot.finance_bot import keyboards as kb
from bot.finance_bot import misc
from bot.finance_bot import reports

from bot.finance_bot.models.currency import dict_currency_reduction
from bot.finance_bot.models.user import list_telegrams_id
from bot.finance_bot.models.currency import dict_currency_reduction_for_search
from bot.finance_bot.models.money import answer_for_user_money
from bot.finance_bot.models.category import creating_dict_for_search_category
from bot.finance_bot.models.category import answer_for_user_category
from bot.finance_bot.models.operations import conversion_operation
from bot.finance_bot.models.operations import account_operation
from bot.finance_bot.models.operations import get_detail_operation_info
from bot.finance_bot.models import investment


def auth_user(func):
    async def wrapper(message):
        if message['from']['id'] not in list_telegrams_id:
            return
        return await func(message)

    return wrapper

@auth_user
async def do_conversion(msg: Message):
    try:
        result, id_operation, answer, old_course = await conversion_operation(
            msg.from_user.id,
            msg.text.lower().replace(',', '.'))
        if result:
            inlines = kb.inline_for_operations(id_operation, old_course)
            await msg.answer(answer, reply_markup=inlines)
        else:
            await msg.answer(f'Ошибка:\n{answer}')
    except Exception as ex:
        await msg.answer(f'Непредвиденная ошибка')

@auth_user
async def do_operation(msg: Message):
    # try:
    answer = await account_operation(
        msg.from_user.id,
        msg.text.lower().replace(',', '.'))
    await msg.answer(**answer)
    # except Exception as ex:
    #     await msg.answer(f'Непредвиденная ошибка')



@auth_user
async def get_currency_list(msg: Message):
    answer = '\n'.join([f'{key}:  {";  ".join(val)}'
                        for key, val in dict_currency_reduction.items()])
    await msg.answer(answer)

@auth_user
async def bt_get_menu(msg: Message):
    answer = msg.text
    await msg.answer(answer, reply_markup=kb.main_menu)

@auth_user
async def bt_get_limits(msg: Message):
    answer = msg.text
    await msg.answer('Лимиты в разработке', reply_markup=kb.main_menu)


@auth_user
async def bt_get_reports(msg: Message):
    tuple_dicts_answers = await reports.get_answer_reports(msg.from_user.id)
    for dict_answer in tuple_dicts_answers:
        await msg.answer(**dict_answer)


@auth_user
async def bt_get_money(msg: Message):
    answer = await answer_for_user_money(msg.from_user.id)
    await msg.answer(answer, reply_markup=kb.main_menu)

@auth_user
async def get_category_list(msg: Message):
    answer = await answer_for_user_category(msg.from_user.id)
    await msg.answer(answer)


@auth_user
async def get_detail_operation(msg: Message):
    operation_type = 'acc' if msg.text[3] == 'a' else 'conv'
    operation_id = int(msg.text[4:])
    answer = await get_detail_operation_info(operation_id, operation_type)
    if answer:
        inlines = kb.inline_for_operations(operation_id, operation_type)
        await msg.answer(answer, reply_markup=inlines)
    else:
        await msg.answer('Операции не существует')


async def create_or_add_investment(message, user_id):
    pass

async def update_price_investment(message, user_id):
    pass

async def subtract_investment(message, user_id):
    pass

async def write_invest(msg: Message, user_id, line):
    operation = ['+', '=', '-']

    message = line.split()
    if any([op in message for op in operation]):
        if len(message) != 5 or not message[3].isdigit():
            await msg.answer('Неверный формат, инвестиция + ИИС 100000 р')
            return
        message[3] = int(message[3])
        result = await investment.start_investment(*message[1:], user_id)
        if result:
            await msg.answer(result)

    elif len(message) == 1:
        result = await investment.get_investment_list(user_id)
        if result:
            await msg.answer(result)

    elif message[1] == '!': # Запись
        result = await investment.get_investment_list(user_id, True)
        if result:
            await msg.answer(result)

    elif len(message) == 3 and message[2] == 'delete':
        result = await investment.delete_investment(message[1], user_id)
        if result:
            await msg.answer(result)
    else:
        await msg.answer('Неизвестная команда')

@auth_user
async def start_investment(msg: Message):
    user_id = msg.from_user.id
    for line in msg.text.split('\n'):
        await write_invest(msg, user_id, line)


inves = [
    'инвестиция',
    'инвестиции',
    'инвест',
    'invest',
]

def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(start_investment, lambda msg: msg.text.lower().split()[0] in inves) # инвестиция
    dp.register_message_handler(get_detail_operation, Text(startswith='/d_')) #do - detail_operation
    dp.register_message_handler(do_conversion, lambda msg:'=' in msg.text)
    dp.register_message_handler(do_operation, regexp=r'\d+')
    dp.register_message_handler(get_currency_list, commands=['currency_all'])
    dp.register_message_handler(get_category_list, commands=['my_categories'])

    dp.register_message_handler(bt_get_menu, Text(equals='Меню'))
    dp.register_message_handler(bt_get_limits, Text(equals='Лимиты'))
    dp.register_message_handler(bt_get_money, Text(equals='Деньги'))
    dp.register_message_handler(bt_get_reports, Text(equals='Отчеты'))
    pass
