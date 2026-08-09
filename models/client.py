from typing import Optional

from pydantic import BaseModel


class Vehicle(BaseModel):
    vin: Optional[str]
    manufacture: Optional[str]
    model: Optional[str]
    year: Optional[int]


class Client(BaseModel):
    id: int
    name: str
    telegram_id: int | None = None
    phone: str | None = None
    vehicle_list: list[Vehicle] | None = None

    def has_any_vehicle(self):
        return self.vehicle_list is not None and len(self.vehicle_list) > 0
