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
from models.client import Client

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
async def cmd_home(message: Message):
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
    if len(client.vehicleList) > 0:
        vehicle_name_list = ""
        for vehicle in client.vehicleList:
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
    await message.answer("")


@client_router.message()
async def message_to_chat(message: Message, client: Client, state: FSMContext):
    logger.debug(f"Current fsm context state is: {await state.get_state()}, "
                 f"fsm context data is: {await state.get_data()}")
    await message.answer("Ваше сообщение отправлено администратору. Скоро Вам ответят, ожидайте.",
                         parse_mode="HTML",
                         reply_markup=keyboards.default_keyboard(True))
