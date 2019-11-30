from models import User
from bot.states import RET
from telebot import TeleBot
from telebot.types import Message
from localization.translations import get_translation_for
from bot.keyboards import get_keyboard_remover
from functools import wraps


def competitor_check(message: Message, user: User, bot: TeleBot, send_message=True):
    competitor = user.check_association()
    if not competitor:
        if send_message:
            bot.send_message(
                message.chat.id,
                get_translation_for('competitor_record_vanished_msg'),
                reply_markup=get_keyboard_remover()
            )
        return {'success': False, 'tuple': (RET.GO_TO_STATE, 'AuthenticationState', message, user)}
    return {'success': True, 'competitor': competitor}


def check_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) == 1:
            ch = competitor_check(
                **kwargs
            )
        elif len(args) == 4:
            ch = competitor_check(
                *args[1:]
            )
        else:
            assert False, "Check_wrapper called used with wrong arguments"
        if ch['success']:
            return func(*args, **kwargs, competitor=ch['competitor'])
        else:
            return ch['tuple']
    return wrapper
