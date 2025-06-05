from aiogram.fsm.state import State, StatesGroup


class RadioSettingsSG(StatesGroup):
    window_start = State()
    window_panel = State()
