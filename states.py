from aiogram.fsm.state import StatesGroup, State


class ClientProfile(StatesGroup):
    change_name = State()
    change_phone = State()
