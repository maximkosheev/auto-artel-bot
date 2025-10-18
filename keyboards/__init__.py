from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

from models.client import Vehicle

def client_default_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🚘 Мои транспортные средства")
    )
    builder.row(
        KeyboardButton(text="📦 Мои заказы")
    )
    return builder.as_markup(resize_keyboard=True)


def client_vehicle_keyboard(vehicles: list | None):
    builder = ReplyKeyboardBuilder()
    if vehicles is not None:
        for vehicle in vehicles:
            builder.row(
                KeyboardButton(text=__build_vehicle_button(vehicle))
            )
    builder.row(KeyboardButton(text="Добавить новое ТС"))
    return builder.as_markup(resize_keyboard=True)


def __build_vehicle_button(vehicle: Vehicle) -> str:
    return f"{vehicle.manufacture} {vehicle.model} {vehicle.year} ({vehicle.vin})"
