import logging

from config import config
from models.chat import ChatMessage
from services.admin_service import JWTAuthInterceptor

logger = logging.getLogger(__name__)

CHAT_MESSAGE_PATH = f"{config.auto_artel_api_base_url}/chat/"


class ChatService:

    def __init__(self):
        self.auth_client = JWTAuthInterceptor()

    async def send_chat_message(self, client_id, chat_message: ChatMessage):
        resp = await self.auth_client.post(CHAT_MESSAGE_PATH, json={
            'client_id': client_id,
            'message': chat_message
        })

        if resp.status == 201:
            return True
        else:
            logger.error(f"Send chat message failed with status: {resp.status}")
            return False

