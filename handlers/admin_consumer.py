import logging

import aio_pika

import config
from models.notices import AutomaticNotice

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

    async def automatic_notice_handler(self):
        queue = await self._channel.declare_queue(name="automatic_notice", durable=True)
        async with queue.iterator() as queue_iter:
            async for notice in queue_iter:
                async with notice.process() as incoming_notice:
                    try:
                        logger.debug("Received notice from 'automatic_notice' queue: {}"
                                     .format(incoming_notice.body))
                        notice = AutomaticNotice.model_validate_json(incoming_notice.body.decode('utf-8'))
                        message = (f"<b>Это системное сообщение от {config.PROJECT_NAME}. "
                                   f"На него не нужно отвечать</b>\n"
                                   f"{notice.data['text']}")
                        await self._bot.send_message(chat_id=notice.to, text=message, parse_mode="HTML")
                    except Exception as e:
                        logger.error("Error occurred while process notice from automatic_notice queue:", exc_info=e)
