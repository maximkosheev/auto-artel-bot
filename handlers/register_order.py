import logging

from aiogram import F
from aiogram import Router
from aiogram.filters import StateFilter, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.state import default_state
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import utils
from keyboards import default_keyboard, cancel_keyboard
from models.client import Client
from services.order_service import OrderService

logger = logging.getLogger(__name__)
register_order_router = Router()
register_order_router.message.filter(MagicData(F.client))


class RegisterOrder(StatesGroup):
    vehicle = State()
    initial_requirements = State()


@register_order_router.message(StateFilter(RegisterOrder), F.text.lower() == "отмена")
async def register_order_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Операция отменена", parse_mode="HTML", reply_markup=default_keyboard(True))


@register_order_router.message(default_state, F.text.lower().contains("новый заказ"))
async def register_order_step1(message: Message, state: FSMContext, client: Client):
    builder = ReplyKeyboardBuilder()
    if client.vehicle_list is not None:
        for vehicle in client.vehicle_list:
            builder.row(
                KeyboardButton(text=utils.build_vehicle_name(vehicle))
            )
    builder.row(KeyboardButton(text="Пропустить"))
    builder.row(KeyboardButton(text="Отмена"))
    await message.answer(text="Выберете транспортное средство из списка",
                         parse_mode="HTML",
                         reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(RegisterOrder.vehicle)


@register_order_router.message(RegisterOrder.vehicle, F.text.lower() == "пропустить")
async def register_order_skip_step1(message: Message, state: FSMContext):
    await state.update_data(vehicle=None)
    await message.answer(text="Опишите, что вам нужно",
                         parse_mode="HTML",
                         reply_markup=cancel_keyboard())
    await state.set_state(RegisterOrder.initial_requirements)


@register_order_router.message(RegisterOrder.vehicle)
async def register_order_step2(message: Message, state: FSMContext):
    await state.update_data(vehicle=message.text)
    await message.answer(text="Опишите, что вам нужно",
                         parse_mode="HTML",
                         reply_markup=cancel_keyboard())
    await state.set_state(RegisterOrder.initial_requirements)


@register_order_router.message(RegisterOrder.initial_requirements)
async def register_order_complete(message: Message, state: FSMContext, client: Client):
    await state.update_data(initial_requirements=message.text)
    try:
        service = OrderService()
        register_data = await state.get_data()
        vehicle_present = register_data['vehicle'] is not None
        registered = await service.register(
            client=client,
            order={
                'initial_requirements': f"{register_data['initial_requirements']} "
                                        f"({'ТС не указано' if not vehicle_present else register_data['vehicle']})"
            }
        )
        if registered:
            await message.answer(text="Заказ создан.\n"
                                      "С вами свяжется менеджер, для уточнения деталей",
                                 parse_mode="HTML",
                                 reply_markup=default_keyboard(True))
        else:
            raise RuntimeError("Заказ не зарегистрирован")
    except Exception as ex:
        logger.error("Failed to register new order", exc_info=ex)
        await message.answer(text="При создании заказа возникла ошибка.",
                             parse_mode="HTML",
                             reply_markup=default_keyboard(True))
    finally:
        await state.clear()
