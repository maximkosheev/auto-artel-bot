import logging
from typing import Dict, Any

from config import config
from models.client import Client
from models.order import Order
from services.admin_service import JWTAuthInterceptor

logger = logging.getLogger(__name__)

ORDERS_PATH = f"{config.auto_artel_api_base_url}/orders/"
LIST_PATH = f"{config.auto_artel_api_base_url}/clients/<client_id>/orders/"
REGISTER_PATH = ORDERS_PATH


class OrderService:
    def __init__(self):
        self.auth_client = JWTAuthInterceptor()

    async def get_all(self, client: Client):
        resp = await self.auth_client.get(LIST_PATH, path_params={
            'client_id': client.id
        })

        if resp.status == 200:
            orders = await resp.json()
            return [Order.model_validate(order) for order in orders]
        else:
            logger.error(f"Get client orders failed with status {resp.status}")
            return None

    async def register(self, client: Client, order: Dict[str, Any]) -> bool:
        resp = await self.auth_client.post(REGISTER_PATH, json={
            'client_id': client.id,
            'initial_requirements': order['initial_requirements']
        })

        if resp.status == 201:
            return True
        else:
            logger.error(f"Register order failed with status {resp.status}")
            return False


order_service = OrderService()
