import asyncio
import logging
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict

import aiohttp
import jwt

from config import config

logger = logging.getLogger(__name__)


class JWTAuthInterceptor:
    def __init__(self):
        self.base_url = config.auto_artel_api_base_url
        self.login_url = f"{self.base_url}/token/"
        self.refresh_url = f"{self.base_url}/token/refresh/"
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
    def session(self) -> aiohttp.ClientSession:
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self._session

    def _is_token_expired(self) -> bool:
        """ Check if access token is expired ore about to expire """
        if not self._access_token or not self._token_expires_at:
            return True

        # Consider token expired if it expires within 30 seconds
        delta_time = timedelta(seconds=30)
        return datetime.now(UTC) + delta_time >= self._token_expires_at

    def _update_token_expiration_time(self):
        claims = jwt.decode(self._access_token, options={"verify_signature": False})
        self._token_expires_at = datetime.fromtimestamp(claims.get("exp"), UTC)

    async def _login(self) -> bool:
        try:
            async with self.session.post(
                    self.login_url,
                    data=self.credentials,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self._access_token = data.get("access")
                    self._refresh_token = data.get("refresh")
                    self._update_token_expiration_time()
                    logger.info("Successfully obtained access token")
                    return True
                else:
                    logger.warning(f"Logging is failed with status code: {response.status}")
                    return False
        except Exception as ex:
            logger.error(f"Loging request failed: {ex}")
            return False

    async def _refresh_access_token(self) -> bool:
        if not self._refresh_token:
            logger.warning("Refresh token is not available. Perform full login")
            return await self._login()

        try:
            async with self.session.post(
                    self.refresh_url,
                    data={'refresh': self._refresh_token},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                if response.status == 200:
                    data = response.json()
                    self._access_token = data.get("access")
                    self._update_token_expiration_time()
                    logger.info("Successfully refresh token")
                else:
                    logger.warning(f"Refresh token failed with status {response.status}")
                    return await self._login()
        except Exception as ex:
            logger.error(f"Refresh request failed: {ex}")
            return await self._login()

    async def _ensure_token_available(self) -> bool:
        async with self._token_lock:
            if self._is_token_expired():
                if self._refresh_token:
                    return await self._refresh_access_token()
                else:
                    return await self._login()
            return True

    async def _handle_auth_retry(self) -> bool:
        return await self._ensure_token_available()

    def _inject_auth_header(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        if headers is None:
            headers_with_auth = {}
        else:
            headers_with_auth = headers.copy()

        if self._access_token:
            headers_with_auth['Authorization'] = f"Bearer {self._access_token}"

        return headers_with_auth

    async def request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        token_available = await self._ensure_token_available()

        if not token_available:
            raise aiohttp.ClientError("Failed to obtain authentication token")

        path_params = kwargs.pop('path_params', {})
        for path_param in path_params:
            url = url.replace(f"<{path_param}>", str(path_params[path_param]))

        headers = kwargs.get('headers', {})
        kwargs['headers'] = self._inject_auth_header(headers)

        logger.debug(f"Send request: {kwargs}")

        try:
            response = await self.session.request(method, url, **kwargs)
            if response.status == 401:
                logger.debug(f"Received 401 for {method} {url}, handling authentication retry")
                await response.release()

                auth_success = await self._handle_auth_retry()
                if not auth_success:
                    raise aiohttp.ClientError("Authentication failed after retry")

                kwargs['headers'] = self._inject_auth_header(headers)
                response = await self.session.request(method, url, **kwargs)

                if response.status == 401:
                    await response.release()
                    raise aiohttp.ClientError("Authentication failed: still receiving 401 after token refresh")

            return response
        except aiohttp.ClientError:
            raise
        except Exception as ex:
            logger.error(f"Request failed with unexpected error: {ex}")
            raise aiohttp.ClientError(f"Request failed: {ex}")

    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        return await self.request('GET', url, **kwargs)

    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        return await self.request('POST', url, **kwargs)

    async def put(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        return await self.request('PUT', url, **kwargs)

    async def delete(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        return await self.request('DELETE', url, **kwargs)

    async def patch(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        return await self.request('PATCH', url, **kwargs)
