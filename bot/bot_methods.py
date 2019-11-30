from models import User
from bot.states import RET
from telebot import TeleBot
from telebot.types import Message
from localization.translations import get_translation_for
from bot.keyboards import get_keyboard_remover
from functools import wraps
from flask_mongoengine.pagination import Pagination
from logger_settings import logger


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


def render_pagination(pagination: Pagination, message: Message, bot: TeleBot, text: str, keyboard_func, update=False, updateText=False):
    if pagination.total:
        available_competitors_encoded_names = []
        for c in pagination.items:
            available_competitors_encoded_names.append(
                [
                    f'{c.name}. {get_translation_for("info_level_str")}: {f"({c.level})"if c.level else "(_)"}.',
                    str(c.id)
                ]
            )
        update_failed = False
        if update:
            try:
                if updateText:
                    bot.edit_message_text(
                        text,
                        message.chat.id,
                        message.message_id,
                        reply_markup=keyboard_func(
                            names=available_competitors_encoded_names,
                            has_pages=pagination.pages > 1,
                            cur_page=pagination.page,
                            pages=pagination.pages,
                            has_next=pagination.has_next,
                            has_prev=pagination.has_prev
                        )
                    )
                else:
                    bot.edit_message_reply_markup(
                        message.chat.id,
                        message.message_id,
                        reply_markup=keyboard_func(
                            names=available_competitors_encoded_names,
                            has_pages=pagination.pages > 1,
                            cur_page=pagination.page,
                            pages=pagination.pages,
                            has_next=pagination.has_next,
                            has_prev=pagination.has_prev
                        )
                    )
            except Exception:
                logger.exception(f'Exception occurred while updating keyboard pagination. Chat: {message.chat.id}')
                update_failed = True
        if not update or update_failed:
            bot.send_message(
                message.chat.id,
                text,
                reply_markup=keyboard_func(
                    names=available_competitors_encoded_names,
                    has_pages=pagination.pages > 1,
                    cur_page=pagination.page,
                    pages=pagination.pages,
                    has_next=pagination.has_next,
                    has_prev=pagination.has_prev
                )
            )
        return True
    return False
