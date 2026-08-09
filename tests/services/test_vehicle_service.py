import unittest
from unittest.mock import patch, AsyncMock

from aiohttp import ClientResponse

from services.vehicle_service import VehicleService, REGISTER_PATH


class TestVehicleService(unittest.IsolatedAsyncioTestCase):

    @patch("services.vehicle_service.JWTAuthInterceptor", new=AsyncMock)
    async def test_register_vehicle(self):
        self.service = VehicleService()
        self.mock_auth_client = self.service.auth_client

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 201
        self.mock_auth_client.post.return_value = mock_response

        # when
        result = await self.service.register(
            client_telegram_id=3,
            vehicle={
                "manufacture": "Ford",
                "model": "Kuga 2",
                "year": 2013,
                "vin": "vin"
            }
        )

        # then
        self.mock_auth_client.post.assert_called_once_with(
            REGISTER_PATH,
            json={
                'client_telegram_id': 3,
                'vehicle': {
                    'manufacture': 'Ford',
                    'model': 'Kuga 2',
                    'year': 2013,
                    'vin': 'vin'
                }
            }
        )
