import re
from functools import lru_cache
from pathlib import Path

from sqlmodel import SQLModel, create_engine

from app_assets import load_users
from app_settings import load_settings
from core.ooh.ooh_loader import load_ooh_template
from core.ooh.ooh_shield import check_ooh_template
from core.radio.radio_loader import load_radio_template
from core.radio.radio_parser import RadioParser
from orm.settings import ESettings
from orm.sql_queries import insert_employee, insert_ooh, insert_radio
from orm.sql_tables import OOH, Employee, Radio  # noqa: F401


def _extract_advertiser(file_name: str) -> str:
    """Извлекает рекламодателя из имени файла."""
    match = re.search(r'^FIXED\s+(.+?)\s+№\d+\.xlsx$', file_name)

    if match:
        return match.group(1)

    raise ValueError(f'Не удалось извлечь рекламодателя из имени файла {file_name}.')


def _create_postgres_url(
    postgres_user: str, postgres_password: str, postgres_host: str, postgres_port: int, postgres_db: str
) -> str:
    """Собирает URL для подключения к Postgres."""
    return f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}'


@lru_cache(maxsize=1)
def get_engine(echo: bool = True):
    """Создает SQLAlchemy-engine."""
    app_settings = load_settings()

    postgres_user = app_settings.POSTGRES_USER
    postgres_password = app_settings.POSTGRES_PASSWORD
    postgres_host = app_settings.POSTGRES_HOST
    postgres_port = app_settings.POSTGRES_PORT
    postgres_db = app_settings.POSTGRES_DB

    url = _create_postgres_url(postgres_user, postgres_password, postgres_host, postgres_port, postgres_db)
    return create_engine(url, echo=echo)


def create_db(engine):
    """Создает базу данных и таблицы."""
    SQLModel.metadata.create_all(engine)


def fill_employee(engine):
    """Заполняет таблицу сотрудников."""
    users = load_users()

    for item in users:
        settings = ESettings().model_dump()
        insert_employee(engine, item['tg_id'], item['username'], item['is_admin'], settings)


def fill_ooh(engine, folder_path: str):
    """Заполняет таблицу OOH."""
    for file_path in Path(folder_path).rglob('*.xlsx'):
        if 'fixed' not in str(file_path).lower():
            continue
        template = load_ooh_template(str(file_path))
        check_ooh_template(template)
        insert_ooh(engine, template)


def fill_radio(engine, folder_path: str):
    """Заполняет таблицу Radio."""
    for file_path in Path(folder_path).rglob('*.xlsx'):
        if 'fixed' not in str(file_path).lower():
            continue

        file_name = file_path.name
        try:
            advertiser = _extract_advertiser(file_name)
        except ValueError:
            raise ValueError(f'Не удалось извлечь рекламодателя из имени файла [{file_name}].')

        parsed_advertiser = RadioParser.parse_advertiser(advertiser)

        if parsed_advertiser is None:
            raise ValueError(f'Не удалось распарсить рекламодателя из имени файла [{file_name}].')

        template = load_radio_template(str(file_path))
        insert_radio(engine, parsed_advertiser, template)


def main():
    engine = get_engine(echo=True)

    create_db(engine)
