import logging

from redis import Redis

from config import config
from datetime import timedelta, datetime, timezone

logger = logging.getLogger(__name__)

CLIENT_CHAT_AUTO_ANSWER_MARKER_KEY = '%d-chat-auto-answer-last-dt'


class CacheService:
    def __init__(self):
        self.connection_url = config.cache_connection_url
        self.connection = None

    def _connect(self):
        self.connection = Redis.from_url(self.connection_url)
        if self.connection.ping():
            logger.info("Successfully connected to Redis")
        else:
            logger.error("Could not connect to Redis")

    def _check_connection(self):
        if self.connection is None:
            self._connect()
        elif not self.connection.ping():
            self.connection.close()
            self._connect()

    def set_client_chat_auto_answer_marker(self, client_telegram_id: int):
        self._check_connection()
        key = CLIENT_CHAT_AUTO_ANSWER_MARKER_KEY.replace('%d', str(client_telegram_id))
        value = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        self.connection.setex(key, timedelta(hours=2), value)

    def check_client_chat_auto_answer_market(self, client_telegram_id: int) -> bool:
        self._check_connection()
        key = CLIENT_CHAT_AUTO_ANSWER_MARKER_KEY.replace('%d', str(client_telegram_id))
        return self.connection.exists(key)

    def check_and_set_client_chat_auto_answer_marker(self, client_telegram_id: int) -> bool:
        """
        Возвращает признак наличия маркера и после этого выставляет его новое значение
        :param client_telegram_id: telegram идентификатор клиента
        :return: предыдущее состояние признака: присутствует/отсутствует
        """
        old_state = self.check_client_chat_auto_answer_market(client_telegram_id)
        self.set_client_chat_auto_answer_marker(client_telegram_id)
        return old_state


cache_service = CacheService()
