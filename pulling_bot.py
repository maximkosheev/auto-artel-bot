import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

from config import config, admins, PROJECT_NAME, BOT_NAME
from handlers import register_client
from handlers.admin_consumer import AdminConsumer
from middlewares.get_client import GetClientMiddleware
from models.client import Client

bot = Bot(token=config.bot_token)
router = Router()
dp = Dispatcher()
admin_consumer = AdminConsumer(config.amq_connection_url, bot)


@router.message(Command("start"))
async def cmd_start(message: Message, client: Client) -> None:
    phrases = [f"Приветствую тебя <b>{message.chat.full_name}</b> в системе <b>{PROJECT_NAME}</b>"]
    if client:
        phrases.append(f"Вы уже зарегистрированы. Для работы воспользуйтесь меню бота")
    else:
        phrases.append("Перед началом работы нужно пройти короткую регистрацию.\nНажмите /register")
    await message.answer(".\n".join(phrases), parse_mode="HTML")


async def notify_admins(message):
    for admin_id in admins:
        await bot.send_message(chat_id=admin_id, text=message)


async def on_startup() -> None:
    await admin_consumer.setup()
    asyncio.create_task(admin_consumer.complete_registration_handler(), name="complete_registration_handler")
    await notify_admins(f"Бот {BOT_NAME} запущен")


async def on_shutdown() -> None:
    await notify_admins(f"Бот {BOT_NAME} остановлен")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()
    await admin_consumer.close()


async def main():
    dp.include_routers(
        router,
        register_client.router
    )
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.message.outer_middleware(GetClientMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s.%(msecs)03d] [%(process)d] [%(levelname)1.1s] [%(name)s]:\t%(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    asyncio.run(main())
