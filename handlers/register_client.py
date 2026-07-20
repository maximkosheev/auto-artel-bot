import logging
import re

from aiogram import F
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.state import default_state
from aiogram.types import Message

from keyboards import cancel_keyboard, default_keyboard
from models.client import Client
from services.clients_service import ClientsService

logger = logging.getLogger(__name__)
register_client_router = Router()


class RegisterClient(StatesGroup):
    name = State()
    phone = State()


@register_client_router.message(StateFilter(None), Command("register"))
@register_client_router.message(default_state, F.text.lower() == "регистрация")
async def register_client_step1(message: Message, state: FSMContext, client: Client):
    if client:
        await message.answer(text="Вы уже зарегистрированы в системе. Для работы воспользуйтесь меню бота",
                             parse_mode="HTML",
                             reply_markup=default_keyboard(True))
        return
    await state.set_state(RegisterClient.name)
    await message.answer(text="Представьтесь, пожалуйста",
                         reply_markup=cancel_keyboard())


@register_client_router.message(StateFilter(RegisterClient), F.text.lower() == "отмена")
async def cancel_registration(message: Message, state: FSMContext, client: Client):
    await state.clear()
    await message.answer("Вы не завершили регистрацию. \n"
                         "Используйте меню бота, чтобы начать регистрацию заново.",
                         parse_mode="HTML",
                         reply_markup=default_keyboard(client is not None))


@register_client_router.message(RegisterClient.name)
async def register_client_step2(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegisterClient.phone)
    await message.answer(text="Спасибо. Теперь напишите телефон для связи в формате +7(десять цифр)",
                         parse_mode="HTML",
                         reply_markup=cancel_keyboard())


@register_client_router.message(RegisterClient.phone)
async def register_client_complete(message: Message, state: FSMContext):
    phone_match = re.match("^\\+7\\d{10}$", message.text)
    if not phone_match:
        return await message.answer("Введите номер телефона в формате +7(десять цифр)")

    await state.update_data(phone=message.text)
    try:
        service = ClientsService()
        register_data = await state.get_data()
        registered = await service.register(client={
            "name": register_data["name"],
            "phone": register_data["phone"],
            "telegram_id": message.from_user.id
        })
        if registered:
            await message.answer(text="Спасибо за регистрацию!\n"
                                      "Для продолжения работы воспользуйтесь меню это бота",
                                 parse_mode="HTML",
                                 reply_markup=default_keyboard(True))
        else:
            await message.answer(text="Простите, но клиент с таким телефоном уже зарегистрирован.\n"
                                      "Обратитесь к администратору",
                                 parse_mode="HTML")
    except Exception as ex:
        logger.error("Failed to register new client", exc_info=ex)
        await message.answer(text="При регистрации случилась ошибка.")
    finally:
        await state.clear()
