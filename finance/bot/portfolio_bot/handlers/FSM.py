from aiogram.dispatcher.filters.state import State, StatesGroup


class CreatePortfolio(StatesGroup):
        name = State()
        answer = State()
