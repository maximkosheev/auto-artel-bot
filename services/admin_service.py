import asyncio
from datetime import datetime, timedelta

import aiohttp
from config import config
from typing import Optional


class JWTAuthInterceptor:
    def __init__(self):
        self.base_url = config.auto_artel_api_base_url
        self.login_url = f"{self.base_url}/login"
        self.refresh_url = f"{self.base_url}/refresh"
        self.credentials = {
            "username": config.auto_artel_api_user,
            "password": config.auto_artel_api_password
        }
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._token_lock = asyncio.Lock()
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    @property
    def session(self):
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self.session

    def _is_token_expired(self):
        """ Check if access token is expired ore about to expire """
        if not self._access_token or not self._token_expires_at:
            return True

        # Consider token expired if it expires within 30 seconds
        delta_time = timedelta(seconds=30)
        return datetime.now() + delta_time >= self._token_expires_at

admin_service = AdminService()
