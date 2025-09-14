import unittest
from unittest.mock import patch, AsyncMock

from aiohttp import ClientResponse

from services.clients_service import ClientsService, CLIENTS_PATH


class TestClientService(unittest.IsolatedAsyncioTestCase):

    @patch("services.clients_service.JWTAuthInterceptor", new=AsyncMock)
    async def test_get_by_telegram_id(self):
        self.service = ClientsService()
        self.mock_auth_client = self.service.auth_client

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.json.return_value = [
            {"id": 1, "telegram_id": "12345", "name": "Alice"}
        ]
        self.mock_auth_client.get.return_value = mock_response
        telegram_id = 3

        # when
        result = await self.service.get_by_telegram_id(telegram_id)

        # then
        self.mock_auth_client.get.assert_called_once_with(
            CLIENTS_PATH, params={'telegram_id': telegram_id}
        )
