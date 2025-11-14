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
    manager: str | None = None
    to: int
    parent_message_id: int | None = None
    text: str
