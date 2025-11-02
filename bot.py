from aiogram import Bot, Dispatcher, Router
from aiogram import F
from aiogram.filters import Command, MagicData
from aiogram.types import Message

import keyboards
from config import config, admins, PROJECT_NAME
from handlers.admin_consumer import AdminConsumer
from handlers.client_handler import client_router
from handlers.register_client import register_client_router
from handlers.register_vehicle import register_vehicle_router

bot = Bot(token=config.bot_token)

router = Router()

out_of_order_router = Router()
out_of_order_router.message.filter(MagicData(F.server_error.is_(True)))
out_of_order_router.callback_query.filter(MagicData(F.server_error.is_(True)))

dp = Dispatcher()
admin_consumer = AdminConsumer(config.amq_connection_url, bot)


@out_of_order_router.message()
async def handle_error(message: Message):
    print(f"Error message: {message.text}")
    await message.answer(f"Случилось что-то нехорошее 😟, но мы уже в курсе и чиним. "
                         f"Скоро сервис снова будет работать!",
                         parse_mode="HTML",
                         reply_markup=keyboards.remove_keyboard())


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    phrases = [f"Приветствую тебя <b>{message.chat.full_name}</b> в системе <b>{PROJECT_NAME}</b>",
               "Перед началом работы нужно пройти короткую регистрацию."]
    await message.answer(".\n".join(phrases), parse_mode="HTML", reply_markup=keyboards.default_keyboard(False))


async def notify_admins(message):
    for admin_id in admins:
        await bot.send_message(chat_id=admin_id, text=message)


def register_routers():
    dp.include_routers(
        out_of_order_router,
        register_client_router,
        register_vehicle_router,
        client_router,
        router
    )
