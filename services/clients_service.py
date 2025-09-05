from admin_service import admin_service

CLIENTS_PATH = "/clients"
REGISTER_PATH = CLIENTS_PATH

class ClientsService:
    async def register(self, client):
        await admin_service.send_request()