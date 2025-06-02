import logging
import sys

# Настройка логирования.
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# Уровень WARNING для избежания засорения логов в терминале.
logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('redis').setLevel(logging.WARNING)

log = logging.getLogger(__name__)


def main() -> None:
    pass


if __name__ == '__main__':
    main()
