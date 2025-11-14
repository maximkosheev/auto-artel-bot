from aiogram.types import Message

from models.chat import ChatMessage


class ChatMessageMapper:

    @classmethod
    def to_chat_message(cls, telegram_message: Message) -> ChatMessage:
        chat_message = ChatMessage(**{
            'id': telegram_message.message_id,
            'from_client_id': telegram_message.from_user.id,
            'reply_to_id': telegram_message.reply_to_message.message_id if telegram_message.reply_to_message is not None else None,
            'text': telegram_message.text
        })
        return chat_message
