import asyncio
import logging

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot import (
    bot,
    dp,
    admin_consumer,
    notify_admins,
    register_routers
)
from config import config
from middlewares.get_client import GetClientMiddleware


async def on_startup() -> None:
    await admin_consumer.setup()
    asyncio.create_task(admin_consumer.automatic_notice_handler(), name="automatic_notice_handler")
    asyncio.create_task(admin_consumer.chat_message_handler(), name="chat_message_handler")
    await bot.set_webhook(config.bot_webhook_uri)
    await notify_admins(f"Бот {config.BOT_NAME} запущен")


async def on_shutdown() -> None:
    await notify_admins(f"Бот {config.BOT_NAME} остановлен")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()
    await admin_consumer.close()


def main():
    register_routers()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.message.outer_middleware(GetClientMiddleware())

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
