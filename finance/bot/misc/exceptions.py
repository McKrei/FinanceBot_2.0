from aiogram.types import CallbackQuery


async def report_message_is_tooLong(callback: CallbackQuery,
                                    answer: dict) -> None:
    all_text = answer['text']
    list_text = all_text.split('+------+')
    if not len(list_text) > 1:
        await callback.answer('Ошибка! Уже сообщил создателю')
        return
    message = ''
    for text in list_text:
        if len(message) < 3000: # МАксимальная длина сообщения в ТГ
            message += text
        else:
            answer['text'] = message
            await callback.message.answer(**answer)
            message = ''
    answer['text'] = message
    await callback.message.answer(**answer)
    await callback.answer()
