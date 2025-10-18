from aiogram import Bot, Dispatcher, Router
from aiogram import F
from aiogram.filters import Command, MagicData
from aiogram.types import Message

from config import config, admins, PROJECT_NAME
from handlers.admin_consumer import AdminConsumer
from models.client import Client
import keyboards

bot = Bot(token=config.bot_token)

router = Router()

client_router = Router()
client_router.message.filter(MagicData(F.client))

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
                         parse_mode="HTML")


@client_router.message(Command("start"))
async def cmd_start_client(message: Message, client: Client):
    phrases = [f"Приветствую тебя <b>{client.name}</b> в системе <b>{PROJECT_NAME}</b>",
               f"Вы уже зарегистрированы. Для работы воспользуйтесь меню бота"]
    await message.answer(".\n".join(phrases), reply_markup=keyboards.client_default_keyboard(), parse_mode="HTML")


@client_router.message()
async def cmd_vehicle(message: Message, client: Client):
    await message.answer("Ща я тебе покажу твои транспортные средства",
                         reply_markup=keyboards.client_vehicle_keyboard(client.vehicleList),
                         parse_mode="HTML")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    phrases = [f"Приветствую тебя <b>{message.chat.full_name}</b> в системе <b>{PROJECT_NAME}</b>",
               "Перед началом работы нужно пройти короткую регистрацию.\nНажмите /register"]
    await message.answer(".\n".join(phrases), parse_mode="HTML")


async def notify_admins(message):
    for admin_id in admins:
        await bot.send_message(chat_id=admin_id, text=message)


