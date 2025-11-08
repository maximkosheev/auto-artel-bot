Запуск тестов:
python -m unittest discover
python -m unittest tests.services.test_order_service
python -m unittest tests.services.test_order_service.TestOrderService
python -m unittest tests.services.test_order_service.TestOrderService.test_get_all_with_fully_filled_order