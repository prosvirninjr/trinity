from aiogram.fsm.state import State, StatesGroup


class OOHSettingsSG(StatesGroup):
    window_start = State()
    window_panel = State()
    window_lower_bound = State()
    window_upper_bound = State()
    window_c_method = State()
    window_s_method = State()
    window_target_year = State()
