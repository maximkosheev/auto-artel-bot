from pydantic import SecretStr, HttpUrl, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_NAME = "The Best Service"
BOT_NAME = "TheBestServiceBot"


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    BOT_WEBHOOK_BASE_URL: str

    AUTO_ARTEL_API_BASE_URL: HttpUrl
    AUTO_ARTEL_API_USER: str
    AUTO_ARTEL_API_PASSWORD: SecretStr

    AMQ_URL: str
    AMQ_USER: str
    AMQ_PASSWORD: SecretStr

    REDIS_URL: str
    REDIS_USER: str
    REDIS_USER_PASSWORD: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    @property
    def bot_token(self) -> str:
        return self.BOT_TOKEN.get_secret_value()

    @property
    def bot_webhook_uri(self):
        return f"{self.BOT_WEBHOOK_BASE_URL}/{self.bot_token}"

    @property
    def webhook_path(self):
        return f"/{self.bot_token}"

    @property
    def auto_artel_api_base_url(self):
        return self.AUTO_ARTEL_API_BASE_URL

    @property
    def auto_artel_api_user(self):
        return self.AUTO_ARTEL_API_USER

    @property
    def auto_artel_api_password(self):
        return self.AUTO_ARTEL_API_PASSWORD.get_secret_value()

    @property
    def amq_connection_url(self):
        credentials = f"{self.AMQ_USER}:{self.AMQ_PASSWORD.get_secret_value()}"
        return self.AMQ_URL.replace("://", f"://{credentials}@")

    @property
    def cache_connection_url(self):
        credentials = f"{self.REDIS_USER}:{self.REDIS_USER_PASSWORD.get_secret_value()}"
        return self.REDIS_URL.replace("://", f"://{credentials}@")


config = Settings()

admins = []
