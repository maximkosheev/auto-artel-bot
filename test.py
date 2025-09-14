import asyncio
import logging

from services.clients_service import ClientsService


async def main():
    client_service = ClientsService()
    await client_service.register(client={
        'name': 'name',
        'phone': '+79089999000'
    })


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
