from aiogram_dialog import DialogManager


async def affinity_task(dialog_manager: DialogManager, **kwargs: object) -> dict[str, object]:
    start_date: str = dialog_manager.dialog_data['start_date']
    end_date: str = dialog_manager.dialog_data['end_date']
    audience: str = dialog_manager.dialog_data['audience']

    return {
        'affinity_params': (
            ('Целевая аудитория', audience),
            ('Дата начала', start_date),
            ('Дата окончания', end_date),
        )
    }
