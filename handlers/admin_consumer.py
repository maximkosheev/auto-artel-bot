import json
import logging

import aio_pika

logger = logging.getLogger(__name__)


class AdminConsumer:
    def __init__(self, connection_url, bot):
        self.connection_url = connection_url
        self._bot = bot
        self._connection = None
        self._channel = None

    async def setup(self):
        self._connection = await aio_pika.connect_robust(url=self.connection_url)
        self._channel = await self._connection.channel()

    async def close(self):
        await self._channel.close()
        await self._connection.close()

    async def complete_registration_handler(self):
        queue = await self._channel.declare_queue(name="registration_completed", durable=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process() as incoming_message:
                    try:
                        logger.debug("Received message from 'registration_completed' queue: {}"
                                     .format(incoming_message.body))
                        data = json.loads(incoming_message.body.decode('utf-8'))
                        logger.info("Client {} finished registration {}"
                                    .format(data["telegram_id"], data["status"]))
                        if data["status"] == "success":
                            await self._bot.send_message(chat_id=data["telegram_id"],
                                                         text="Аккаунт FatSecret.com успешно подключен")
                        else:
                            await self._bot.send_message(chat_id=data["telegram_id"],
                                                         text="При подключении аккаунта FatSecret.com возникла ошибка. "
                                                              "Попробуйте позже или обратитесь к администратору.")
                    except Exception as e:
                        logger.error("Error occurred while process message from registration_completed queue: {}".format(e))
