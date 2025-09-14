import logging
from typing import Any, Dict

from config import config
from .admin_service import JWTAuthInterceptor

logger = logging.getLogger(__name__)


CLIENTS_PATH = f"{config.auto_artel_api_base_url}/clients/"
REGISTER_PATH = CLIENTS_PATH


class ClientsService:

    def __init__(self):
        self.auth_client = JWTAuthInterceptor()

    async def register(self, client: Dict[str, Any]):
        resp = await self.auth_client.post(REGISTER_PATH, json=client)
        if resp.status == 201:
            return True
        else:
            logger.error(f"Register user failed with status: {resp.status}")
            return False

    async def get_by_telegram_id(self, telegram_id):
        resp = await self.auth_client.get(CLIENTS_PATH, params={
            'telegram_id': telegram_id
        })
        if resp.status == 200:
            clients = await resp.json()
            print(f"Received clients: {clients}")
        else:
            logger.error(f"Get client by telegram_id failed with status: {resp.status}")
