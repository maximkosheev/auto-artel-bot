import logging

from config import config
from models.chat import ChatMessage
from services.admin_service import JWTAuthInterceptor

logger = logging.getLogger(__name__)

CHAT_MESSAGE_PATH = f"{config.auto_artel_api_base_url}/chat/"
UPDATE_CHAT_MESSAGE_PATH = f"{CHAT_MESSAGE_PATH}message/<message_id>/"


class ChatService:

    def __init__(self):
        self.auth_client = JWTAuthInterceptor()

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

    async def update_chat_message(self, message_id, data: dict):
        resp = await self.auth_client.patch(UPDATE_CHAT_MESSAGE_PATH,
                                            path_params={
                                                'message_id': message_id
                                            },
                                            json=data)

        if resp.status == 200:
            return True
        else:
            logger.error(f"Update chat message failed with status: {resp.status}")
            return False
