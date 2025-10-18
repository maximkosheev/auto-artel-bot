import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from services.clients_service import ClientsService

logger = logging.getLogger(__name__)


class GetClientMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]):
        try:
            telegram_id = event.from_user.id
            service = ClientsService()
            data['client'] = await service.get_by_telegram_id(telegram_id)
            logger.info(f"Client: {data['client']}")
        except Exception as ex:
            logger.error("Failed to get client by telegram_id", exc_info=ex)
            data['server_error'] = True
        finally:
            return await handler(event, data)
