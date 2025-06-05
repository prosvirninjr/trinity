import asyncio
import concurrent.futures
import functools
from collections.abc import Callable
from typing import Any


# WARNING: Использовать исключительно для CPU-bound задач.
async def run_in_process(sync_func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """
    Запускает синхронную CPU-bound функцию в отдельном процессе и возвращает результат её выполнения.

    Args:
        sync_func (Callable[..., Any]): Синхронная функция.
        *args (Any): Позиционные аргументы для функции.
        **kwargs (Any): Именованные аргументы для функции.

    Returns:
        Any: Результат выполнения функции.
    """
    # Получаем текущий цикл событий.
    loop = asyncio.get_running_loop()

    func_to_run = functools.partial(sync_func, *args, **kwargs)

    # Запускаем функцию в отдельном процессе (CPU-bound).
    with concurrent.futures.ProcessPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, func_to_run)

    return result
