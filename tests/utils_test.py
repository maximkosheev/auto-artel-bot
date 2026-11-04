import unittest

from models.order import Order
import utils
import datetime


class TestUtils(unittest.TestCase):
    def test_build_order_info_new_status(self):
        order_data = {
            'id': 123,
            'client_status': 'Новый',
            'created': datetime.datetime.fromisoformat('2025-11-07T19:07:00+00:00'),
            'initial_requirements': 'Хочу масляный фильтр',
        }
        order = Order(**order_data)
        order_info = utils.build_order_info(order)
        self.assertEqual('Номер: 123 от 2025-11-07, статус: Новый', order_info)

    def test_build_order_info_in_progress_status(self):
        order_data = {
            'id': 123,
            'client_status': 'В работе',
            'created': datetime.datetime.fromisoformat('2025-11-07T19:07:00+00:00'),
            'manager': 'Иванов Иван',
            'initial_requirements': 'Хочу масляный фильтр',
            'order_item_list': [
                {
                    'id': 1111,
                    'price': '1234.45'
                }
            ]
        }
        order = Order(**order_data)
        order_info = utils.build_order_info(order)
        self.assertEqual('Номер: 123 от 2025-11-07, статус: В работе, количество позиций: 1, общая стоимость: 1234.45', order_info)
