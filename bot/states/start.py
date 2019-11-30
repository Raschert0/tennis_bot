from . import RET, BaseState
from localization.translations import get_translation_for

from telebot import TeleBot
from telebot.types import Message
from models import User

from bot.keyboards import get_keyboard_remover


class StartState(BaseState):
    has_entry = False

    def process_message(self, message: Message, user: User, bot: TeleBot):
        bot.send_message(message.chat.id,
                         get_translation_for('welcome_msg').format(user.username or user.first_name),
                         reply_markup=self.__base_keyboard()
                         )
        return RET.GO_TO_STATE, 'AuthenticationState', message, user

    def __base_keyboard(self, **kwargs):
        return get_keyboard_remover()
