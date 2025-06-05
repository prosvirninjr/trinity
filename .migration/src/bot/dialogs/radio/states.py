from aiogram.fsm.state import State, StatesGroup


class RadioTaskSG(StatesGroup):
    window_start = State()
