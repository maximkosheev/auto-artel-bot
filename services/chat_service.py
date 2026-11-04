import logging
from typing import Optional

from config import config
from models.chat import ChatMessage
from services.admin_service import jwt_auth_interceptor

logger = logging.getLogger(__name__)

CHAT_MESSAGE_PATH = f"{config.auto_artel_api_base_url}/chat/"
UPDATE_CHAT_MESSAGE_PATH = f"{CHAT_MESSAGE_PATH}message/"


class ChatService:

    def __init__(self):
        self.auth_client = jwt_auth_interceptor

    async def send_chat_message(self, client_id, chat_message: ChatMessage):
        resp = await self.auth_client.post(CHAT_MESSAGE_PATH, json={
            'client_id': client_id,
            'message': chat_message.model_dump()
        })

        if resp.status == 201:
            return True
        else:
            logger.error(f"Send chat message failed with status: {resp.status}")
            return False

    async def update_chat_message(self,
                                  data: dict,
                                  message_id: Optional[int] = None,
                                  message_telegram_id: Optional[int] = None):
        if message_id is None and message_telegram_id is None:
            raise KeyError('The message_id or the message_telegram_id parameter must be specified')
        if message_id is not None and message_telegram_id is not None:
            raise KeyError('Either the message_id or the message_telegram_id could be specified')

        resp = await self.auth_client.patch(UPDATE_CHAT_MESSAGE_PATH,
                                            params={
                                                'id': message_id,
                                                'telegram_id': message_telegram_id
                                            },
                                            json=data)

        if resp.status == 200:
            return True
        else:
            logger.error(f"Update chat message failed with status: {resp.status}")
            return False


chat_service = ChatService()
