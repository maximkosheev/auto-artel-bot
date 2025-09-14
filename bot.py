import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import config, admins
from handlers import register_client
from handlers.admin_consumer import AdminConsumer

router = Router()

bot = Bot(token=config.bot_token)
dp = Dispatcher()
admin_consumer = AdminConsumer(config.amq_uri, bot)

NAME = "The best service"


@router.message(Command("start"))
async def cmd_start(message: Message, client: Client) -> None:
    phrases = [f"Приветствую тебя <b>{message.chat.full_name}</b> в системе <b>{NAME}</b>"]
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
    await bot.set_webhook(config.bot_webhook_uri)
    await notify_admins('Бот AutoArtelBot запущен')


async def on_shutdown() -> None:
    await notify_admins("Бот AutoArtelBot остановлен")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()
    await admin_consumer.close()


def main():
    dp.include_routers(
        router,
        register_client.router
    )
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=config.webhook_path)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=9000)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s.%(msecs)03d] [%(process)d] [%(levelname)1.1s] [%(name)s]:\t%(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    main()
