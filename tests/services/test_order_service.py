import unittest
from decimal import Decimal
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

from aiohttp import ClientResponse

from models.client import Client
from models.order import Order
from services.order_service import OrderService, LIST_PATH


class TestOrderService(unittest.IsolatedAsyncioTestCase):

    @patch("services.order_service.JWTAuthInterceptor", new=AsyncMock)
    async def test_get_all_with_fully_filled_order(self):
        self.service = OrderService()
        self.mock_auth_client = self.service.auth_client

        client = Client.model_construct(**{'id': 1})

        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.json.return_value = [
            {
                'id': 123,
                'client_status': 'В процессе',
                'manager': 'Иванов',
                'created': '2025-11-06T12:00:00Z',
                'initial_requirements': 'initial_requirements',
                'order_item_list': [
                    {
                        'id': 111,
                        'article_number': 'order_item_1_article_number',
                        'manufacture': 'order_item_1_manufacture',
                        'name': 'order_item_1_name',
                        'price': '11000.45'
                    }
                ]
            }
        ]

        self.mock_auth_client.get.return_value = mock_response

        # when
        result = await self.service.get_all(client)

        # then
        self.mock_auth_client.get.assert_called_once_with(LIST_PATH, path_params={'client_id': 1})
        expected_data = {
            'id': 123,
            'client_status': 'В процессе',
            'manager': 'Иванов',
            'created': datetime(2025, 11, 6, 12, 0, 0, 0, timezone.utc),
            'initial_requirements': 'initial_requirements',
            'order_item_list': [
                {
                    'id': 111,
                    'article_number': 'order_item_1_article_number',
                    'manufacture': 'order_item_1_manufacture',
                    'name': 'order_item_1_name',
                    'price': Decimal('11000.45')
                }
            ]
        }
        expected = [Order(**expected_data)]
        self.assertListEqual(expected, result)
