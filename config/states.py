from aiogram.dispatcher.filters.state import State, StatesGroup


class CheckAddress(StatesGroup):
    eth = State()
    bsc = State()
