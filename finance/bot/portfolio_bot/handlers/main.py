from aiogram import Dispatcher

from bot.portfolio_bot.handlers.user import register_user_handlers
from bot.portfolio_bot.handlers.callback import register_callback_handlers


def portfolio_register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_user_handlers,
        # register_callback_handlers
    )
    for handler in handlers:
        handler(dp)
