from enum import Enum
from typing import Any

from pydantic import BaseModel


class AutomaticNoticeType(Enum):
    TEXT = 1


class AutomaticNotice(BaseModel):
    to: int
    type: AutomaticNoticeType
    data: dict[str, Any]


class ChatNotice(BaseModel):
    # идентификатор сообщения в БД
    id: int
    # идентификатор клиента в БД, которому направляется сообщение
    to: int
    # Идентификатор чата с клиентом в Telegram
    to_telegram_id: int
    # Имя менеджера, который отправил сообщение
    manager: str | None = None
    # Собственно текст сообщения
    text: str
    # Идентификатор сообщения в Telegram, в ответ на который пришло это сообщение
    reply_to_telegram_id: int | None = None
