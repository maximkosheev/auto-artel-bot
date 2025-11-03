import datetime

from pydantic import BaseModel, Field


class Order(BaseModel):
    id: int = Field()
    client_status: str = Field()
    manager: str = Field(default="Не назначен")
    created: datetime.datetime


