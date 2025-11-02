from typing import Optional

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from models.client import Vehicle


def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True
    )


def skip_and_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пропустить")],
            [KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True
    )


def remove_keyboard():
    return ReplyKeyboardRemove()


def client_default_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🚘 Мои транспортные средства")
    )
    builder.row(
        KeyboardButton(text="📦 Мои заказы")
    )
    return builder.as_markup(resize_keyboard=True)


def anonymous_default_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="Регистрация")
    )
    return builder.as_markup(resize_keyboard=True)


def default_keyboard(is_registered):
    return client_default_keyboard() if is_registered else anonymous_default_keyboard()


def client_vehicle_keyboard(vehicles: Optional[list]):
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
