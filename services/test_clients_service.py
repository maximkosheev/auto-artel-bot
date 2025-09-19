import unittest
from unittest.mock import patch, AsyncMock

from aiohttp import ClientResponse

from exceptions import AutoArtelHttpException
from services.clients_service import ClientsService, DETAIL_PATH


class TestClientService(unittest.IsolatedAsyncioTestCase):

    @patch("services.clients_service.JWTAuthInterceptor", new=AsyncMock)
    async def test_get_by_telegram_id(self):
        self.service = ClientsService()
        self.mock_auth_client = self.service.auth_client

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.json.return_value = [
            {
                "name": "ClientName1",
                "telegram_id": "12345",
                "phone": "79999999999",
                "vehicleList": [
                    {
                        "vin": "1234567890",
                        "manufacture": "Manufacture1",
                        "model": "Model1",
                        "year": 2000
                    }
                ]
            },
            {
                "name": "ClientName2",
                "telegram_id": "12346",
                "phone": "78888888888",
                "vehicleList": [
                    {
                        "vin": "0987654321",
                        "manufacture": "Manufacture2",
                        "model": "Model2",
                        "year": 2001
                    }
                ]
            }
        ]
        self.mock_auth_client.get.return_value = mock_response
        telegram_id = 3

        # when
        result = await self.service.get_by_telegram_id(telegram_id)

        # then
        self.mock_auth_client.get.assert_called_once_with(
            DETAIL_PATH, params={'telegram_id': telegram_id}
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "ClientName1")
        self.assertEqual(result.telegram_id, 12345)
        self.assertEqual(result.phone, "79999999999")
        self.assertEqual(len(result.vehicleList), 1)
        self.assertEqual(result.vehicleList[0].vin, "1234567890")
        self.assertEqual(result.vehicleList[0].manufacture, "Manufacture1")
        self.assertEqual(result.vehicleList[0].model, "Model1")
        self.assertEqual(result.vehicleList[0].year, 2000)

    @patch("services.clients_service.JWTAuthInterceptor", new=AsyncMock)
    async def test_get_by_telegram_id_empty_response(self):
        self.service = ClientsService()
        self.mock_auth_client = self.service.auth_client

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.json.return_value = []
        self.mock_auth_client.get.return_value = mock_response
        telegram_id = 3

        # when
        result = await self.service.get_by_telegram_id(telegram_id)

        # then
        self.mock_auth_client.get.assert_called_once_with(
            DETAIL_PATH, params={'telegram_id': telegram_id}
        )
        self.assertIsNone(result)

    @patch("services.clients_service.JWTAuthInterceptor", new=AsyncMock)
    async def test_get_by_telegram_id_error_response(self):
        self.service = ClientsService()
        self.mock_auth_client = self.service.auth_client

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 504
        self.mock_auth_client.get.return_value = mock_response
        telegram_id = 3

        # when
        with self.assertRaises(AutoArtelHttpException) as e:
            await self.service.get_by_telegram_id(telegram_id)

        # then
        self.mock_auth_client.get.assert_called_once_with(
            DETAIL_PATH, params={'telegram_id': telegram_id}
        )
        self.assertEqual(str(e.exception), "Server response with error")
