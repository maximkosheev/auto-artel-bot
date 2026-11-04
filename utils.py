from models.client import Vehicle
from models.order import Order


def build_vehicle_name(vehicle: Vehicle) -> str:
    return f"{vehicle.manufacture} {vehicle.model} {vehicle.year} ({vehicle.vin})"


def build_order_info(order: Order) -> str:
    base_info = f"Номер: {order.id} от {order.created.date()}, статус: {order.client_status}"
    if order.order_item_list is not None and len(order.order_item_list) > 0:
        amount = sum(item.price for item in order.order_item_list if item.price is not None)
        return f"{base_info}, количество позиций: {len(order.order_item_list)}, общая стоимость: {amount}"
    else:
        return base_info
