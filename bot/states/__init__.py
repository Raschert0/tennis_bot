from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from localization.translations import get_translation_for
from models import User
from enum import IntEnum


class RET(IntEnum):
    OK = 1
    GO_TO_STATE = 2
    ANSWER_CALLBACK = 3
    ANSWER_AND_GO_TO_STATE = 4


class BaseState(object):
    has_entry = True
    accepts_everything = False
    # needs_authentication = True

    def __init__(self):
        # self._buttons = {'back_btn': self.back_button}
        self._buttons = {}

    def __base_keyboard(self, **kwargs):
        return None

    def entry(self, message: Message, user: User, bot: TeleBot):
        return RET.OK, None, None, None

    def process_message_with_buttons(self, message: Message, user: User, bot: TeleBot):
        # if self.authentication_required(user):
        #     return RET_GO_TO_STATE, 'AuthenticationState', message, user
        if message.text:
            for k, v in self._buttons.items():
                assert user.language is not None
                if message.text == get_translation_for(k):
                    ret = v(message, user, bot)
                    if isinstance(ret, tuple):
                        return ret
                    break
        return self.process_message(message, user, bot)

    # def authentication_required(self, user):
    #     if not self.needs_authentication:
    #         return False
    #     return not check_auth(user)

    def process_message(self, message: Message, user: User, bot: TeleBot):
        bot.send_message(message.chat.id,
                         get_translation_for('use_keyboard_msg'),
                         reply_markup=self.__base_keyboard()
                         )
        return RET.OK, None, None, None

    def process_callback(self, callback:CallbackQuery, user, bot: TeleBot):
        bot.answer_callback_query(callback.id)
        return RET.OK, None, None, None

    # Buttons

    def back_button(self, message: Message, user: User, bot: TeleBot):
        if len(user.states) > 1:
            user.states.pop()  # current state
            move_to = user.states.pop()
            user.save()
            return RET.GO_TO_STATE, move_to, message, user
        return RET.GO_TO_STATE, 'AuthenticationState', message, user

    def main_menu_btn(self, message: Message, user: User, bot: TeleBot):
        return RET.GO_TO_STATE, 'AuthenticationState', message, user
