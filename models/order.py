import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    id: int
    article_number: str | None = None
    manufacture: str | None = None
    name: str | None = None
    price: Decimal | None = None


class Order(BaseModel):
    id: int | None = None
    client_status: str = "Новый"
    manager: str = "Не назначен"
    created: datetime.datetime | None = None
    initial_requirements: str
    order_item_list: list[OrderItem] | None = None

