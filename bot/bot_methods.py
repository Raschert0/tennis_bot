from models import User, Competitor
from bot.states import RET
from telebot import TeleBot
from telebot.types import Message
from localization.translations import get_translation_for
from bot.keyboards import get_keyboard_remover, get_menu_keyboard
from functools import wraps
from flask_mongoengine.pagination import Pagination
from logger_settings import logger
from config import STATES_HISTORY_LEN


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


def get_opponent_and_opponent_user(competitor: Competitor) -> (Competitor, User):
    opponent: Competitor = competitor.check_opponent()
    opponent_user = User.objects(associated_with=opponent).first() if opponent else None
    return opponent, opponent_user


def teardown_challenge(
        competitor: Competitor,
        message: Message,
        user: User,
        bot: TeleBot,
        cause_key,
        canceled_by_bot=True,
        opponent: Competitor = None,
        opponent_msg_key=None
):
    competitor.in_challenge_with = None
    competitor.status = competitor.previous_status
    competitor.previous_status = None
    competitor.latest_challenge_received_at = None
    competitor.save()

    if opponent:
        opponent_user = User.objects(associated_with=opponent).first()

        opponent.in_challenge_with = None
        opponent.status = opponent.previous_status
        opponent.previous_status = None
        opponent.latest_challenge_received_at = None
        opponent.save()

        if opponent_user:

            opponent_user.dismiss_confirmed = False
            opponent_user.states.append('MenuState')
            if len(opponent_user.states) > STATES_HISTORY_LEN:
                del opponent_user.states[0]
            opponent_user.save()

            if opponent_msg_key:
                if canceled_by_bot:
                    bot.send_message(
                        opponent_user.user_id,
                        f'{get_translation_for(opponent_msg_key).format(competitor.name)}.\n{get_translation_for("challenge_confirm_challenge_canceled_by_bot_msg")}',
                        reply_markup=get_menu_keyboard(status=opponent.status),
                        parse_mode='html'
                    )
                else:
                    bot.send_message(
                        opponent_user.user_id,
                        f'{get_translation_for(opponent_msg_key).format(competitor.name)}',
                        reply_markup=get_menu_keyboard(status=opponent.status),
                        parse_mode='html'
                    )

    user.dismiss_confirmed = False
    user.save()

    if cause_key is not None:
        if canceled_by_bot:
            bot.send_message(
                user.user_id,
                f'{get_translation_for(cause_key)}.\n{get_translation_for("challenge_confirm_challenge_canceled_by_bot_msg")}'
            )
        else:
            bot.send_message(
                user.user_id,
                f'{get_translation_for(cause_key)}'
            )
    return RET.GO_TO_STATE, 'MenuState', message, user
