from models.client import Vehicle


def build_vehicle_name(vehicle: Vehicle) -> str:
    return f"{vehicle.manufacture} {vehicle.model} {vehicle.year} ({vehicle.vin})"
