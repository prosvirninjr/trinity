import asyncio

from aiogram import Bot


async def send_action(bot: Bot, chat_id: int, task: asyncio.Task, action: str = 'typing') -> None:
    """
    Воспроизводит в чате указанное действие до тех пор, пока не завершится отслеживаемая задача.

    Args:
        bot: Экземпляр бота Aiogram.
        chat_id: ID чата, в котором воспроизводится действие.
        task: Задача, по завершении которой прекращается воспроизведение действия.
        action: Тип действия, которое будет воспроизводиться (по умолчанию 'typing').
    """
    while not task.done():
        await bot.send_chat_action(chat_id=chat_id, action=action)
        await asyncio.sleep(5)
