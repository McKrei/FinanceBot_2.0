from aiogram import Dispatcher
from aiogram.types import Message
import re


async def processing_message(msg: Message):
    print(msg.from_user.id)
    await msg.answer('Пролетел')


def register_other_handlers(dp: Dispatcher) -> None:
    # todo: register all other handlers

    dp.register_message_handler(processing_message, content_types=['text'])
