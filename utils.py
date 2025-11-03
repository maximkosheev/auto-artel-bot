from models.client import Vehicle
from models.order import Order


def build_vehicle_name(vehicle: Vehicle) -> str:
    return f"{vehicle.manufacture} {vehicle.model} {vehicle.year} ({vehicle.vin})"


def build_order_info(order: Order) -> str:
    return f""
