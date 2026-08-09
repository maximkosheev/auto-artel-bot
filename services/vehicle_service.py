import logging
from typing import Dict, Any

from config import config
from services.admin_service import JWTAuthInterceptor

VEHICLE_PATH = f"{config.auto_artel_api_base_url}/vehicle/"
REGISTER_PATH = VEHICLE_PATH

logger = logging.getLogger(__name__)


class VehicleService:

    def __init__(self):
        self.auth_client = JWTAuthInterceptor()

    async def register(self, client_telegram_id, vehicle: Dict[str, Any]) -> bool:
        resp = await self.auth_client.post(REGISTER_PATH, json={
            "client_telegram_id": client_telegram_id,
            "vehicle": vehicle
        })

        if resp.status == 201:
            return True
        else:
            logger.error(f"Register vehicle failed with status: {resp.status}")
            return False

