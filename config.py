from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    BOT_BASE_URL: SecretStr

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


config = Settings()

admins = []
