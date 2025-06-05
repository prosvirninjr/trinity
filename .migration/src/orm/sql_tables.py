from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.sqltypes import BigInteger
from sqlmodel import Field, SQLModel


class Employee(SQLModel, table=True):
    """
    Таблица с сотрудниками.

    Содержит информацию о сотрудниках, их настройки и права доступа.
    """

    id: int | None = Field(default=None, primary_key=True)
    tg_id: int = Field(sa_type=BigInteger, unique=True)
    username: str
    is_admin: bool = Field(default=False)
    settings: dict = Field(sa_type=JSONB)


class OOH(SQLModel, table=True):
    """
    Таблица с шаблонами OOH.

    Содержит обработанные шаблоны OOH в формате JSONB.
    """

    id: int | None = Field(default=None, primary_key=True)
    template: dict | list[dict] = Field(sa_type=JSONB)


class Radio(SQLModel, table=True):
    """
    Таблица с шаблонами Radio.

    Содержит обработанные шаблоны Radio в формате JSONB.
    """

    id: int | None = Field(default=None, primary_key=True)
    template: dict = Field(sa_type=JSONB)
