from typing import Any, Dict

from config import config
from .admin_service import JWTAuthInterceptor
import logging


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
