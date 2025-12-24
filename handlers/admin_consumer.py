import logging

import aio_pika

import config
from models.notices import AutomaticNotice, ChatNotice
from services.chat_service import ChatService

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

    async def chat_message_handler(self):
        queue = await self._channel.declare_queue(name="chat_messages", durable=True)
        async with queue.iterator() as queue_iter:
            async for chat_notice in queue_iter:
                async with chat_notice.process() as incoming_notice:
                    try:
                        logger.debug(f"Received message from 'chat_messages' queue: {incoming_notice.body}")
                        incoming_message = ChatNotice.model_validate_json(incoming_notice.body.decode('utf-8'))
                        message = (f"<b>Вам отвечает менеджер {incoming_message.manager}</b>\n"
                                   f"{incoming_message.text}")
                        msg = await self._bot.send_message(
                            chat_id=incoming_message.to_telegram_id,
                            text=message,
                            parse_mode="HTML",
                            reply_to_message_id=incoming_message.reply_to_telegram_id
                        )
                        chat_service = ChatService()
                        await chat_service.update_chat_message(incoming_message.id, {
                            'telegram_id': msg.message_id
                        })
                    except Exception as e:
                        logger.error("Error occurred while process notice from 'chat_messages' queue:", e)
