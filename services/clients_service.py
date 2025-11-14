import logging
from typing import Any, Dict

from config import config
from exceptions import AutoArtelHttpException
from models.client import Client
from .admin_service import JWTAuthInterceptor

logger = logging.getLogger(__name__)


CLIENTS_PATH = f"{config.auto_artel_api_base_url}/clients/"
REGISTER_PATH = CLIENTS_PATH
DETAIL_PATH = f"{CLIENTS_PATH}<telegram_id>/detail/"


class ClientsService:

    def __init__(self):
        self.auth_client = JWTAuthInterceptor()

    async def register(self, client: Dict[str, Any]) -> bool:
        resp = await self.auth_client.post(REGISTER_PATH, json=client)
        if resp.status == 201:
            return True
        else:
            logger.error(f"Register user failed with status: {resp.status}")
            return False

    async def get_by_telegram_id(self, telegram_id) -> Client | None:
        resp = await self.auth_client.get(DETAIL_PATH, path_params={
            'telegram_id': telegram_id
        })
        if resp.status == 200:
            client = await resp.json()
            return Client.model_validate(client, strict=True)
        elif resp.status == 404:
            return None
        else:
            logger.error(f"Get client by telegram_id failed with status: {resp.status}")
            raise AutoArtelHttpException("Server response with error")