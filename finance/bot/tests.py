from bot.database.models import *




async def test_models_methods():
    await create_user(1)
    await create_user(2)
    u = await get_user(1)
    print('Пользователь №1', u)
    # print('все users', await get_user())

    # await create_goal(1, 'спорт', 1000)
    # await create_goal(1, 'работа', 1000, 'week')
