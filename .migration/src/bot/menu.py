from textwrap import dedent

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import BotCommand, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import ManagedMultiselect, ManagedRadio

from bot.dialogs.ooh.states import OOHTaskSG
from bot.dialogs.ooh_settings.states import OOHSettingsSG
from bot.dialogs.radio.states import RadioTaskSG
from bot.dialogs.radio_settings.states import RadioSettingsSG
from bot.dialogs.tv.ru import states
from orm.settings import ESettings
from orm.sql_builder import get_engine
from orm.sql_queries import select_employee
from orm.sql_tables import Employee

router = Router()


async def set_commands(bot: Bot) -> None:
    """Инициализирует основные команды."""
    commands: list[BotCommand] = [
        BotCommand(command='/start', description='Старт'),
        BotCommand(command='/help', description='Помощь'),
        BotCommand(command='/nat_base_task', description='Нац. ТВ: осн. выгрузка'),
        BotCommand(command='/nat_affinity_task', description='Нац. ТВ: avg. affinity'),
        BotCommand(command='/reg_base_task', description='Рег. ТВ: осн. выгрузка'),
        BotCommand(command='/reg_affinity_task', description='Рег. ТВ: avg. affinity'),
        BotCommand(command='/ooh_settings', description='OOH: Настройки'),
        BotCommand(command='/ooh_task', description='OOH: Расчет'),
        BotCommand(command='/radio_task', description='Радио: Расчет'),
        BotCommand(command='/radio_settings', description='Радио: Настройки'),
    ]

    await bot.set_my_commands(commands)


@router.message(Command('start'))
async def cmd_start(message: Message) -> None:
    """Хендлер команды /start."""
    username: str = message.from_user.username or 'Незнакомец'  # type: ignore

    text = dedent(
        f"""
        Привет, {username}. Я бот-ассистент.
        
        Что я умею?
        - Обрабатывать выгрузки из Нац. и Рег. ТВ.
        - Выгружать avg. affinity для Нац. и Рег. ТВ.
        - Создавать отчет OOH.
        - Создавать отчет Радио.

        Как со мной работать?
        
        Работа со мной происходит через команды.
        Список доступных команд можно получить с помощью /help.

        Используй /help для справки.
        """
    )
    await message.answer(text=text)


@router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    """Хендлер команды /help."""
    text = dedent(
        """
        Взаимодействие с ботом происходит через команды.
        
        На данный момент доступны следующие команды:
        
        /start - Начало работы с ботом.
        /help - Помощь по работе с ботом.
        /nat_base_task - Нац. ТВ: осн. выгрузка.
        /nat_affinity_task - Нац. ТВ: avg. affinity.
        /reg_base_task - Рег. ТВ: осн. выгрузка.
        /reg_affinity_task - Рег. ТВ: avg. affinity.
        /ooh_settings - OOH: Настройки.
        /ooh_task - OOH: Расчет.

        По вопросам и предложениям обращайтесь к @prosvirninjr.
        """
    )
    await message.answer(text=text)


@router.message(Command('nat_base_task'))
async def cmd_nat_base_task(message: Message, dialog_manager: DialogManager) -> None:
    """Хендлер команды /nat_base_task."""
    await dialog_manager.start(state=states.NatBaseTaskSG.window_start, mode=StartMode.RESET_STACK)


@router.message(Command('nat_affinity_task'))
async def cmd_nat_affinity_task(message: Message, dialog_manager: DialogManager) -> None:
    """Хендлер команды /nat_affinity_task."""
    await dialog_manager.start(state=states.NatAffinityTaskSG.window_audience, mode=StartMode.RESET_STACK)


@router.message(Command('reg_base_task'))
async def cmd_reg_base_task(message: Message, dialog_manager: DialogManager) -> None:
    """Хендлер команды /reg_base_task."""
    await dialog_manager.start(state=states.RegBaseTaskSG.window_start, mode=StartMode.RESET_STACK)


@router.message(Command('reg_affinity_task'))
async def cmd_reg_affinity_task(message: Message, dialog_manager: DialogManager) -> None:
    """Хендлер команды /reg_affinity_task."""
    await dialog_manager.start(state=states.RegAffinityTaskSG.window_audience, mode=StartMode.RESET_STACK)


@router.message(Command('ooh_settings'))
async def cmd_ooh_settings(message: Message, dialog_manager: DialogManager) -> None:
    """Хендлер команды /ooh_settings."""
    await dialog_manager.start(state=OOHSettingsSG.window_start, mode=StartMode.RESET_STACK)  # type: ignore

    _panel: ManagedMultiselect = dialog_manager.find('_panel')  # type: ignore
    _s_method: ManagedRadio = dialog_manager.find('_s_method')  # type: ignore
    _c_method: ManagedRadio = dialog_manager.find('_c_method')  # type: ignore
    _target_year: ManagedRadio = dialog_manager.find('_target_year')  # type: ignore

    engine = get_engine()
    employee: Employee = select_employee(engine=engine, tg_id=message.from_user.id)  # type: ignore
    e_settings = ESettings.model_validate(employee.settings)

    # Панель.
    for item_id in e_settings.ooh.panel:
        await _panel.set_checked(item_id=item_id, checked=True)  # type: ignore

    # Метод сглаживания.
    await _s_method.set_checked(item_id=e_settings.ooh.s_method)  # type: ignore

    # Метод расчета.
    await _c_method.set_checked(item_id=e_settings.ooh.c_method)  # type: ignore

    # Целевой год.
    await _target_year.set_checked(item_id=e_settings.ooh.target_year)  # type: ignore


@router.message(Command('ooh_task'))
async def cmd_ooh_create_task(message: Message, dialog_manager: DialogManager) -> None:  # noqa
    """Хендлер команды /ooh_task."""
    await dialog_manager.start(state=OOHTaskSG.window_start, mode=StartMode.RESET_STACK)  # type: ignore


@router.message(Command('radio_task'))
async def cmd_radio_create_task(message: Message, dialog_manager: DialogManager) -> None:  # noqa
    """Хендлер команды /radio_task."""
    await dialog_manager.start(state=RadioTaskSG.window_start, mode=StartMode.RESET_STACK)  # type: ignore


@router.message(Command('radio_settings'))
async def cmd_radio_settings(message: Message, dialog_manager: DialogManager) -> None:  # noqa
    """Хендлер команды /radio_settings."""
    await dialog_manager.start(state=RadioSettingsSG.window_start, mode=StartMode.RESET_STACK)  # type: ignore
