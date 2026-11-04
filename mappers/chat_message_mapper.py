from aiogram.types import Message

from models.chat import ChatMessage


class ChatMessageMapper:

    @classmethod
    def to_chat_message(cls, telegram_message: Message) -> ChatMessage:
        if telegram_message.reply_to_message:
            reply_to_id = telegram_message.reply_to_message.message_id
        else:
            reply_to_id = None

        chat_message = ChatMessage(**{
            'message_telegram_id': telegram_message.message_id,
            'reply_to_message_telegram_id': reply_to_id,
            'text': telegram_message.text
        })
        return chat_message
