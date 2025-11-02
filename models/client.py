from typing import Optional

from pydantic import BaseModel


class Vehicle(BaseModel):
    vin: Optional[str]
    manufacture: Optional[str]
    model: Optional[str]
    year: Optional[int]


class Client(BaseModel):
    name: str
    telegram_id: int
    phone: str
    vehicleList: list[Vehicle]
