import os

from aiogram.utils import executor
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from env import TgKeys
from bot.finance_bot.handlers import register_all_handlers
from bot.portfolio_bot.handlers import portfolio_register_all_handlers



async def __on_start_up(dp: Dispatcher) -> None:
    portfolio_register_all_handlers(dp)
    register_all_handlers(dp)


def runbot():
    bot = Bot(token=TgKeys.TOKEN, parse_mode='HTML')
    dp = Dispatcher(bot, storage=MemoryStorage())
    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)
