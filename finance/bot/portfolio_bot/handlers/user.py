from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from bot.portfolio_bot.handlers import FSM
from bot.finance_bot.keyboards import main_menu
from bot.portfolio_bot import keyboards as kb
from bot.portfolio_bot import misc
from bot.portfolio_bot import reports

from portfolio.models import Portfolio

from bot.finance_bot.models.user import list_telegrams_id
def auth_user(func):
    async def wrapper(msg):
        if msg['from']['id'] not in list_telegrams_id:
            return
        return await func(msg)

    return wrapper


# @auth_user
async def get_invest(msg: Message):
    mes = 'Для добавления нового портфеля жми /Create_portfolio'
    await msg.answer(mes, reply_markup=main_menu)


@auth_user
async def create_portfolio_start(msg: Message):
    await FSM.CreatePortfolio.name.set()
    await msg.reply('Напиши название портфеля')


async def create_portfolio_name(msg: Message, state: FSMContext):
    name = msg.text
    async with state.proxy() as data:
        data['name'] = name
    await FSM.CreatePortfolio.answer.set()
    await msg.reply(f'Создаю портфель: {name}\n/yes\n/Cancel')


async def create_portfolio_answer(msg: Message, state: FSMContext):
    p = Portfolio()
    async with state.proxy() as data:
        result, mes = await p.create(name=data['name'], tgid=msg.from_user.id)
    await state.finish()
    await msg.reply(mes)


async def cancel_handler(msg: Message, state: FSMContext):
    current_state = state.get_state()
    if current_state is None:
        return
    await state.finish()
    await msg.reply(f'Ок!')


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(
        get_invest, Text(equals='Инвестиции'))
    dp.register_message_handler(
        create_portfolio_start, commands=['Create_portfolio'], state=None)
    dp.register_message_handler(
        create_portfolio_name, state=FSM.CreatePortfolio.name)
    dp.register_message_handler(
        create_portfolio_answer, commands=['yes'], state=FSM.CreatePortfolio.answer)
    dp.register_message_handler(
        cancel_handler,commands=['Cancel'], state='*')
    dp.register_message_handler(
        cancel_handler, Text(equals='отмена', ignore_case=True), state='*')
