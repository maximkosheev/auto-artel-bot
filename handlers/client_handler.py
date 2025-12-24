import logging

from aiogram import F
from aiogram import Router
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import Message

import keyboards
import utils
from config import PROJECT_NAME
from mappers.chat_message_mapper import ChatMessageMapper
from models.client import Client
from services.chat_service import ChatService
from services.order_service import order_service

logger = logging.getLogger(__name__)

client_router = Router()
client_router.message.filter(MagicData(F.client))


@client_router.message(Command("start"))
async def cmd_start_client(message: Message, client: Client):
    phrases = [f"Приветствую тебя <b>{client.name}</b> в системе <b>{PROJECT_NAME}</b>",
               f"Вы уже зарегистрированы. Для работы воспользуйтесь меню бота"]
    await message.answer(".\n".join(phrases),
                         parse_mode="HTML",
                         reply_markup=keyboards.default_keyboard(True))


@client_router.message(F.text.lower().contains('в начало'))
async def cmd_home(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню",
                         parse_mode="HTML",
                         reply_markup=keyboards.default_keyboard(True))


@client_router.message(F.text.lower().contains('мои транспортные средства'))
async def cmd_vehicles(message: Message, client: Client):
    kb = [
        [KeyboardButton(text="🚗 Регистрация нового ТС")],
        [KeyboardButton(text="↩️ В начало")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    if client.has_any_vehicle():
        vehicle_name_list = ""
        for vehicle in client.vehicle_list:
            vehicle_name_list += f"\t - {utils.build_vehicle_name(vehicle)}\n"
        await message.answer("Вот список ваших зарегистрированных транспортных средств:\n"
                             f"{vehicle_name_list}",
                             reply_markup=keyboard,
                             parse_mode="HTML")
    else:
        await message.answer("У вас пока нет ни одного зарегистрированного ТС.\n"
                             "Воспользуйтесь меню для регистрации",
                             reply_markup=keyboard,
                             parse_mode="HTML")


@client_router.message(F.text.lower().contains('мои заказы'))
async def cmd_orders(message: Message, client: Client):
    kb = [
        [KeyboardButton(text="Новый заказ")],
        [KeyboardButton(text="↩️ В начало")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    orders = await order_service.get_all(client)
    if orders and len(orders) > 0:
        orders_info = ""
        for order in orders:
            orders_info += f"\t - {utils.build_order_info(order)}\n"
        await message.answer("Вот ваши заказы:\n"
                             f"{orders_info}",
                             parse_mode="HTML",
                             reply_markup=keyboard)
    else:
        await message.answer("У вас пока нет ни одного заказа",
                             parse_mode="HTML",
                             reply_markup=keyboard)


@client_router.message()
async def message_to_chat(message: Message, client: Client):
    service = ChatService()
    chat_message = ChatMessageMapper.to_chat_message(message)
    send = await service.send_chat_message(client.id, chat_message)
    if send:
        await message.answer("Ваше сообщение отправлено администратору. Скоро Вам ответят, ожидайте.",
                             parse_mode="HTML",
                             reply_markup=keyboards.default_keyboard(True))
    else:
        await message.answer("Не удалось отправить сообщение администратору. Попробуйте позже.",
                             parse_mode="HTML",
                             reply_markup=keyboards.default_keyboard(True))
