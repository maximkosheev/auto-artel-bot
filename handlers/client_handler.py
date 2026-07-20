import logging
import re

from aiogram import F
from aiogram import Router
from aiogram.filters import Command, MagicData, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import Message

import keyboards
import utils
from config import PROJECT_NAME
from mappers.chat_message_mapper import ChatMessageMapper
from models.client import Client
from services.cache_service import cache_service
from services.chat_service import chat_service
from services.clients_service import ClientsService
from services.order_service import order_service
from states import ClientProfile

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


@client_router.message(F.text.lower().contains('мой профиль'))
async def cmd_profile(message: Message, client: Client):
    kb = [
        [KeyboardButton(text=f"Изменить имя")],
        [KeyboardButton(text=f"Изменить телефон")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Вы можете изменить Ваше имя и телефон.\n"
                         f"Текущее имя: {client.name}\n"
                         f"Текущий телефон: {client.phone}",
                         reply_markup=keyboard,
                         parse_mode="HTML")


@client_router.message(StateFilter(ClientProfile), F.text.lower() == "отмена")
async def cmd_change_profile_cancel(message: Message, state: FSMContext, client:Client):
    await state.clear()
    await message.answer('Операция отменена',
                         parse_mode='HTML',
                         reply_markup=keyboards.default_keyboard(True))


@client_router.message(StateFilter(None), default_state, F.text.lower() == 'изменить имя')
async def cmd_change_name_init(message: Message, state: FSMContext, client:Client):
    await state.set_state(ClientProfile.change_name)
    await message.answer("Представьтесь, пожалуйста",
                         parse_mode='HTML',
                         reply_markup=keyboards.cancel_keyboard())


@client_router.message(ClientProfile.change_name)
async def cmd_change_name(message: Message, state: FSMContext, client:Client):
    await state.update_data(name=message.text)
    try:
        service = ClientsService()
        profile_data = await state.get_data()
        updated = await service.update_profile(client.id, profile={
            'name': profile_data['name']
        })
        if updated:
            await message.answer('Ваше имя успешно изменено',
                                 parse_mode='HTML',
                                 reply_markup=keyboards.default_keyboard(True))
        else:
            await message.answer('Изменить имя не получилось. Обратитесь к администратору',
                                 parse_mode='HTML',
                                 reply_markup=keyboards.default_keyboard(True))
    except Exception as ex:
        logger.error("Failed to update client profile", exc_info=ex)
        await message.answer("При обновлении профиля случилась ошибка. Попробуйте ещё раз позже.",
                             parse_mode='HTML',
                             reply_markup=keyboards.default_keyboard(True))
    finally:
        await state.clear()


@client_router.message(StateFilter(None), default_state, F.text.lower() == 'изменить телефон')
async def cmd_change_phone_init(message: Message, state: FSMContext, client:Client):
    await state.set_state(ClientProfile.change_phone)
    await message.answer("Укажите телефон для связи в формате +7XXXXXXXXXX(десять цифр)",
                         parse_mode='HTML',
                         reply_markup=keyboards.cancel_keyboard())


@client_router.message(ClientProfile.change_phone)
async def cmd_change_phone(message: Message, state: FSMContext, client:Client):
    phone_match = re.match("^\\+7\\d{10}$", message.text)
    if not phone_match:
        return await message.answer("Неверный формат. Введите номер телефона в формате +7XXXXXXXXXX(десять цифр)",
                                    parse_mode='HTML',
                                    reply_markup=keyboards.cancel_keyboard())

    await state.update_data(phone=message.text)
    try:
        service = ClientsService()
        profile_data = await state.get_data()
        updated = await service.update_profile(client.id, profile={
            'phone': profile_data['phone']
        })
        if updated:
            await message.answer('Номер телефона успешно изменено',
                                 parse_mode='HTML',
                                 reply_markup=keyboards.default_keyboard(True))
        else:
            await message.answer('Изменить номер телефона не получилось.\n'
                                 'Вероятно клиент с таким номером телефона уже зарегистрирован.\n'
                                 'Обратитесь к администратору',
                                 parse_mode='HTML',
                                 reply_markup=keyboards.default_keyboard(True))
    except Exception as ex:
        logger.error("Failed to update client profile", exc_info=ex)
        await message.answer("При обновлении профиля случилась ошибка. Попробуйте ещё раз позже.",
                             parse_mode='HTML',
                             reply_markup=keyboards.default_keyboard(True))
    finally:
        await state.clear()



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
    chat_message = ChatMessageMapper.to_chat_message(message)
    send = await chat_service.send_chat_message(client.id, chat_message)
    if send:
        if not cache_service.check_and_set_client_chat_auto_answer_marker(message.from_user.id):
            await message.answer("Ваше сообщение отправлено администратору. Скоро Вам ответят, ожидайте.",
                                 parse_mode="HTML",
                                 reply_markup=keyboards.default_keyboard(True))
    else:
        await message.answer("Не удалось отправить сообщение администратору. Попробуйте позже.",
                             parse_mode="HTML",
                             reply_markup=keyboards.default_keyboard(True))


@client_router.edited_message()
async def message_to_chat_edited(message: Message):
    updated = await chat_service.update_chat_message(message_telegram_id=message.message_id, data={
        'text': message.text
    })
    if not updated:
        logger.warning(f"Message telegram_id: {message.message_id} was not updated")
