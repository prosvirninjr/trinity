from datetime import datetime

from pydantic import BaseModel, Field

from core.ooh.schema import CMethod, SMethod


class OOHSettings(BaseModel):
    """Настройки OOH."""

    panel: list[str] = []  # Список рекламодателей.
    s_method: str = SMethod.mean  # Метод сглаживания.
    c_method: str = CMethod.default  # Метод расчета.
    target_year: int = datetime.now().year  # Год для расчета инфляции.


class RadioSettings(BaseModel):
    """Настройки Radio."""

    panel: list[str] = []  # Список рекламодателей.


class ESettings(BaseModel):
    """Настройки пользователя."""

    ooh: OOHSettings = Field(default_factory=OOHSettings)
    radio: RadioSettings = Field(default_factory=RadioSettings)
