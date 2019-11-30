from models import User
from logger_settings import logger
from bot.states import RET
from localization.translations import get_translation_for
from localization.translations import create_translation
from helpers import user_last_state
from telebot.types import Message, CallbackQuery, User as TGUser
import telebot
import config

from bot.states.start import StartState
from bot.states.authentication import AuthenticationState
from bot.states.menu import MenuState


class BotHandlers(object):

    def __init__(self, token):
        self.bot = telebot.TeleBot(token, threaded=False)
        self.__states = {}
        self.__start_state = 'StartState'
        self.__register_states(
            StartState,
            MenuState,
            AuthenticationState,
        )
        self.__start_handling()

    def __get_or_register_user(self, chat_id, tg_user: TGUser):
        user = User.objects(user_id=chat_id).first()
        if user is None:
            user = User(user_id=chat_id,
                        user_id_s=str(chat_id),
                        username=tg_user.username,
                        first_name=tg_user.first_name,
                        last_name=tg_user.last_name,
                        states=[self.__start_state],
                        language='ww',
                        )
            user.save()
        return user

    def __start_handling(self):

        def for_private_chats_only(message):
            if isinstance(message, Message):
                if message.chat.type != 'private':
                    return False
            elif isinstance(message, CallbackQuery):
                if message.message.chat.type != 'private':
                    return False
            return True

        def for_public_chats_only(message):
            return not for_private_chats_only(message)

        def blocked_check(chat, user):
            if user.is_blocked:
                self.bot.send_message(chat.id,
                                      get_translation_for('blocked_msg')
                                      )
                return True

        @self.bot.message_handler(commands=['start'], func=for_private_chats_only)
        def send_welcome(message):
            try:
                user = self.__get_or_register_user(message.chat.id, message.from_user)
                user.states = [self.__start_state]
                user.save()

                if blocked_check(message.chat, user):
                    return

                self.__process_message(message, user)
            except:
                logger.exception("Error!")

        @self.bot.message_handler(content_types=['text'], func=for_private_chats_only)
        def text_handler(message):
            try:
                user = self.__get_or_register_user(message.chat.id, message.from_user)
                if blocked_check(message.chat, user):
                    return
                self.__process_message(message, user)
            except:
                logger.exception("Error!")

        @self.bot.message_handler(content_types=['audio', 'document', 'photo', 'sticker', 'video', 'video_note',
                                                 'voice', 'contact'], func=for_private_chats_only)
        def everything_handler(message):
            try:
                user = self.__get_or_register_user(message.chat.id, message.from_user)
                if blocked_check(message.chat, user):
                    return
                state_correct, current_state, c_name = self.__get_state(user_last_state(user, self.__start_state))
                if not state_correct:
                    user.states = [c_name]
                    user.save()
                    self.__process_message(message, user)
                else:
                    if current_state.accepts_everything:
                        self.__process_message(message, user)
                    else:
                        self.bot.send_message(
                            message.chat.id,
                            get_translation_for('message_type_not_supported_msg')
                        )
            except:
                logger.exception("Error!")

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_inline(reply: CallbackQuery):
            try:
                user = self.__get_or_register_user(reply.from_user.id, reply.from_user)
                if blocked_check(reply.message.chat, user):
                    return
                self.__process_callback(reply, user)
            except:
                logger.exception("Error!")

    def __register_state(self, state_class):
        self.__states[state_class.__name__] = state_class()

    def __register_states(self, *states):
        for state in states:
            self.__register_state(state)

    def __get_state(self, name):
        if callable(name):
            name = name.__name__
        ret = self.__states.get(name)
        if ret is None:
            logger.error('No state with name "{}"'.format(name))
            return False, self.__states[self.__start_state], self.__start_state
        return True, ret, name

    def __process_ret_code(self, ret_tuple):
        """
        :param ret_tuple:
            ret_tuple[0] - ret code
            ret_tuple[1] - ret value
            ret_tuple[2] - message, callback or None
            ret_tuple[3] - user or None
        :return:
        """
        if ret_tuple[0] == RET.OK:
            return

        if ret_tuple[0] == RET.GO_TO_STATE:
            self.__send_user_to_state(ret_tuple[2], ret_tuple[3], ret_tuple[1])
        elif ret_tuple[0] == RET.ANSWER_CALLBACK:
            self.bot.answer_callback_query(ret_tuple[2].id, text=ret_tuple[1])
        elif ret_tuple[0] == RET.ANSWER_AND_GO_TO_STATE:
            self.bot.answer_callback_query(ret_tuple[2].id)
            self.__send_user_to_state(ret_tuple[2].message, ret_tuple[3], ret_tuple[1])

    def __process_message(self, message, user):
        state_correct, current_state, c_name = self.__get_state(user_last_state(user, self.__start_state))
        if not state_correct:
            user.states = [c_name]
            user.save()
        try:
            self.__process_ret_code(current_state.process_message_with_buttons(message, user, self.bot))
        except:
            logger.exception(self.__get_state(user_last_state(user, 'Unknown state')))

    def __process_callback(self, callback, user):
        state_correct, current_state, c_name = self.__get_state(user_last_state(user, self.__start_state))
        if not state_correct:
            user.states = [c_name]
            user.save()
        try:
            self.__process_ret_code(current_state.process_callback(callback, user, self.bot))
        except:
            logger.exception(self.__get_state(user_last_state(user, 'Unknown state')))

    def __send_user_to_state(self, message, user, state):
        state_correct, current_state, c_name = self.__get_state(state)
        user.states.append(c_name)
        if len(user.states) > config.STATES_HISTORY_LEN:
            del user.states[0]
        user.save()
        try:
            if current_state.has_entry:
                self.__process_ret_code(current_state.entry(message=message, user=user, bot=self.bot))
            else:
                self.__process_ret_code(current_state.process_message_with_buttons(message=message, user=user, bot=self.bot))
        except:
            logger.exception(self.__get_state(user_last_state(user, 'Unknown state')))


bot_handler = BotHandlers(config.BOT_TOKEN)
if __name__ == '__main__':
    create_translation()
    bot_handler.bot.remove_webhook()
    bot_handler.bot.polling(none_stop=True)
