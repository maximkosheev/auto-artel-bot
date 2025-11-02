import logging
import re
from datetime import date

from aiogram import F
from aiogram import Router
from aiogram.filters import StateFilter, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.state import default_state
from aiogram.types import Message

from keyboards import cancel_keyboard, skip_and_cancel_keyboard, default_keyboard
from services.vehicle_service import VehicleService

logger = logging.getLogger(__name__)
register_vehicle_router = Router()
register_vehicle_router.message.filter(MagicData(F.client))


class RegisterVehicle(StatesGroup):
    manufacture = State()
    model = State()
    year = State()
    vin = State()


@register_vehicle_router.message(StateFilter(RegisterVehicle), F.text.lower() == "отмена")
async def register_vehicle_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Операция отменена", parse_mode="HTML", reply_markup=default_keyboard(True))


@register_vehicle_router.message(default_state, F.text.lower().contains("регистрация нового тс"))
async def register_vehicle_step1(message: Message, state: FSMContext):
    await message.answer(text="Укажите производителя ТС",
                         parse_mode="HTML",
                         reply_markup=cancel_keyboard())
    await state.set_state(RegisterVehicle.manufacture)


@register_vehicle_router.message(RegisterVehicle.manufacture)
async def register_vehicle_step2(message: Message, state: FSMContext):
    await state.update_data(manufacture=message.text)
    await state.set_state(RegisterVehicle.model)
    await message.answer(text="Укажите модель ТС",
                         parse_mode="HTML",
                         reply_markup=cancel_keyboard())


@register_vehicle_router.message(RegisterVehicle.model)
async def register_vehicle_step3(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(RegisterVehicle.year)
    await message.answer(text="Укажите год выпуска",
                         parse_mode="HTML",
                         reply_markup=cancel_keyboard())


@register_vehicle_router.message(RegisterVehicle.year)
async def register_vehicle_step4(message: Message, state: FSMContext):
    year_match = re.match("^\\d{4}$", message.text)
    if not year_match:
        return await message.answer("Укажите год выпуска в формате 'yyyy'",
                                    parse_mode="HTML",
                                    reply_markup=cancel_keyboard())
    year = int(message.text)
    if year < 1900 or year > date.today().year:
        return await message.answer("Указан некорректный год выпуска",
                                    parse_mode="HTML",
                                    reply_markup=cancel_keyboard())

    await state.update_data(year=year)
    await state.set_state(RegisterVehicle.vin)
    await message.answer(text="Укажите VIN номер. \n"
                              "Если не знаете, можно пропустить этот шаг, но он очень поможет при заказах",
                         parse_mode="HTML",
                         reply_markup=skip_and_cancel_keyboard())


@register_vehicle_router.message(RegisterVehicle.vin, F.text.lower() == "пропустить")
async def register_vehicle_skip_step5(message: Message, state: FSMContext):
    await state.update_data(vin=None)
    await register_vehicle_complete(message, state)


@register_vehicle_router.message(RegisterVehicle.vin)
async def register_vehicle_step5(message: Message, state: FSMContext):
    await state.update_data(vin=message.text)
    await register_vehicle_complete(message, state)


async def register_vehicle_complete(message: Message, state: FSMContext):
    try:
        service = VehicleService()
        register_data = await state.get_data()
        registered = await service.register(
            client_telegram_id=message.from_user.id,
            vehicle={
                "manufacture": register_data["manufacture"],
                "model": register_data["model"],
                "year": register_data["year"],
                "vin": register_data["vin"]
            })
        if registered:
            await message.answer(text="Новое транспортное средство зарегистрировано",
                                 parse_mode="HTML",
                                 reply_markup=default_keyboard(True))
    except Exception as ex:
        logger.error("Failed to register new vehicle", exc_info=ex)
        await message.answer(text="При регистрации транспортного средства возникла ошибка.",
                             parse_mode="HTML",
                             reply_markup=default_keyboard(True))
    finally:
        await state.clear()
