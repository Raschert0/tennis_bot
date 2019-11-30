from models import User
from bot.states import RET
from telebot import TeleBot
from telebot.types import Message
from localization.translations import get_translation_for
from bot.keyboards import get_keyboard_remover


def competitor_check(message: Message, user: User, bot: TeleBot, send_message=True):
    if not user.associated_with:
        if send_message:
            bot.send_message(
                message.chat.id,
                get_translation_for('competitor_record_vanished_msg'),
                reply_markup=get_keyboard_remover()
            )
        return False, [RET.GO_TO_STATE, 'AuthenticationState', message, user]
    return True, None
