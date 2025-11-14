from pydantic import BaseModel


class ChatMessage(BaseModel):
    id: int
    from_client_id: int
    reply_to_id: int
    text: str | None = None
    media: list[str] | None = None
