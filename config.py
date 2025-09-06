from pydantic import SecretStr, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    BOT_BASE_URL: SecretStr
    AUTO_ARTEL_API_BASE_URL: HttpUrl
    AUTO_ARTEL_API_USER: str
    AUTO_ARTEL_API_PASSWORD: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    @property
    def bot_token(self) -> str:
        return self.BOT_TOKEN.get_secret_value()

    @property
    def bot_webhook_uri(self):
        return self.BOT_WEBHOOK_URI.get_secret_value()

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


config = Settings()

admins = []
