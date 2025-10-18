import asyncio
import logging

from bot import (
    bot,
    dp,
    router,
    out_of_order_router,
    admin_consumer,
    notify_admins
)
from config import BOT_NAME
from handlers import register_client
from middlewares.get_client import GetClientMiddleware


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
        out_of_order_router,
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
