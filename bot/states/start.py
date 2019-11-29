from . import RET, BaseState
from localization.translations import get_translation_for

from telebot import TeleBot
from telebot.types import Message
from models import User


class StartState(BaseState):
    has_entry = False

    def __init__(self):
        super().__init__()
        self._buttons = {}
        self._base_keyboard = None

    def process_message(cls, message: Message, user: User, bot: TeleBot):
        bot.send_message(message.chat.id,
                         get_translation_for('welcome_msg').format(user.username or user.first_name)
                         )
        return RET.GO_TO_STATE, 'AuthenticationState', message, user
