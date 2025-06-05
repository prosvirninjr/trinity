from aiogram.fsm.state import State, StatesGroup


class NatBaseTaskSG(StatesGroup):
    window_start = State()


class NatAffinityTaskSG(StatesGroup):
    window_audience = State()
    window_start_date = State()
    window_end_date = State()
    window_confirm = State()


class RegBaseTaskSG(StatesGroup):
    window_start = State()


class RegAffinityTaskSG(StatesGroup):
    window_audience = State()
    window_start_date = State()
    window_end_date = State()
    window_confirm = State()
