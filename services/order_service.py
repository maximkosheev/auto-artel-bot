import logging
from services.admin_service import JWTAuthInterceptor
from config import config

logger = logging.getLogger(__name__)

ORDERS_PATH = f"{config.auto_artel_api_base_url}/orders/"
LIST_PATH = ORDERS_PATH


class OrderService:
    def __init__(self):
        self.auth_client = JWTAuthInterceptor()

    async def get_all(self, client_telegram_id):
        resp = await self.auth_client.get(LIST_PATH, path_params={
            'client_telegram_id': client_telegram_id
        })

        if resp.status == 200:
            return []
        else:
            logger.error(f"Get client orders failed with status {resp.status}")
            return None


order_service = OrderService()
