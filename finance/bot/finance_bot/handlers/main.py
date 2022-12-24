from aiogram import Dispatcher

from bot.finance_bot.handlers.other import register_other_handlers
from bot.finance_bot.handlers.user import register_user_handlers
from bot.finance_bot.handlers.callback import register_callback_handlers




def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_user_handlers,
        register_other_handlers,
        register_callback_handlers
    )
    for handler in handlers:
        handler(dp)
