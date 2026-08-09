from pydantic import BaseModel


class ChatMessage(BaseModel):
    message_telegram_id: int
    reply_to_message_telegram_id: int | None = None
    text: str
    media: list[str] | None = None
