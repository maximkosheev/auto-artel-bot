import logging
import re

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, User
from models.client import Client
from services.clients_service import ClientsService

logger = logging.getLogger(__name__)
router = Router()


class RegisterClient(StatesGroup):
    name = State()
    phone = State()


@router.message(Command("register"))
async def register_client_step1(message: Message, state: FSMContext, client: Client):
    if client:
        await message.answer(text="Вы уже зарегистрированы в системе. Для работы воспользуйтесь меню бота",
                             parse_mode="HTML")
        return
    await message.answer(text="Представьтесь, пожалуйста")
    await state.set_state(RegisterClient.name)


@router.message(RegisterClient.name)
async def register_client_step2(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text="Спасибо. Теперь напишите телефон для связи в формате +7XXXXXXXXXX", parse_mode="HTML")
    await state.set_state(RegisterClient.phone)


@router.message(RegisterClient.phone)
async def register_client_complete(message: Message, state: FSMContext):
    phone_match = re.match("^\\+7\\d{10}$", message.text)
    if not phone_match:
        return await message.answer("Введите номер телефона в формате +7XXXXXXXXXX")

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
                                 parse_mode="HTML")
        else:
            await message.answer(text="Простите, но клиент с таким телефоном уже зарегистрирован.\n"
                                      "Обратитесь к администратору",
                                 parse_mode="HTML")
    except Exception as ex:
        logger.error("Failed to register new client", exc_info=ex)
        await message.answer(text="При регистрации случилась ошибка.")
    finally:
        await state.clear()
