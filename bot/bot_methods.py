from models import User, Competitor, Result, RESULT, COMPETITOR_STATUS
from bot.states import RET
from telebot import TeleBot
from telebot.types import Message
from telebot.apihelper import ApiException
from localization.translations import get_translation_for
from bot.keyboards import get_keyboard_remover, get_menu_keyboard
from functools import wraps
from flask_mongoengine.pagination import Pagination
from logger_settings import logger
from config import STATES_HISTORY_LEN, BOT_TOKEN
from google_integration.sheets.logs import LogsSheet
from bot.settings_interface import get_config
from json import loads


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
            except ApiException as e:
                j = loads(e.result.text)
                if j['description'].find('is not modified') != -1:
                    logger.warning(f'Pagination update resulted in the same message. New message is not sent: {message.chat.id}')
                else:
                    logger.exception(f'Exception occurred while updating keyboard pagination. Chat: {message.chat.id}')
                    update_failed = True
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
        message,
        user: User,
        bot: TeleBot,
        cause_key,
        canceled_by_bot=True,
        opponent: Competitor = None,
        opponent_msg_key=None,
        no_glog=False
):
    competitor.in_challenge_with = None
    competitor.change_status(competitor.previous_status)
    competitor.previous_status = None
    competitor.latest_challenge_received_at = None
    competitor.save()

    if opponent:
        opponent_user = User.objects(associated_with=opponent).first()

        opponent.in_challenge_with = None
        opponent.change_status(opponent.previous_status)
        opponent.previous_status = None
        opponent.latest_challenge_received_at = None
        opponent.save()

        if canceled_by_bot and not no_glog:
            LogsSheet.glog(get_translation_for('gsheet_log_challenge_canceled').format(competitor.name, opponent.name))

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
    else:
        if canceled_by_bot and not no_glog:
            LogsSheet.glog(get_translation_for('gsheet_log_challenge_canceled_no_opponent').format(competitor.name))

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


def render_result(res: Result, final=False):
    text = get_translation_for('result_current_str')+':\n'
    rr = res.scores
    scorepairs = [[]]
    for s in rr:
        if len(scorepairs[-1]) >= 2:
            scorepairs.append([s])
        else:
            scorepairs[-1].append(s)
            if len(scorepairs[-1]) == 2 and not final and res.result is None:
                scorepairs.append([])

    for sp in scorepairs:
        if len(sp) == 0:
            text += f'X-_'
        if len(sp) == 1:
            text += f'{sp[0]}-X'
        if len(sp) == 2:
            text += f'{sp[0]}-{sp[1]}'
        text += '\n'

    text += '\n'
    if final:
        if res.result is not None:
            text += get_translation_for('result_to_change_winner_press_again_str')
        else:
            text += get_translation_for('result_select_winner_str')
        text += '\n'

    if res.result is not None:
        text += '\n'
        text += f'<b>{get_translation_for("result_match_result_str")}: '
        c = None
        if res.result == RESULT.A_WINS:
            c = f'{res.player_a.fetch().name} {get_translation_for("result_wins_str")} {res.player_b.fetch().name}'
        elif res.result == RESULT.B_WINS:
            c = f'{res.player_b.fetch().name} {get_translation_for("result_wins_str")} {res.player_a.fetch().name}'
        elif res.result == RESULT.CANCELED:
            c = get_translation_for('result_challenge_canceled_str')

        if c:
            text += c
        text += '</b>'
    return text


def send_msg_to_admin(msg):
    try:
        cfg = get_config()
        if not cfg.admin_username:
            return
        bot = TeleBot(BOT_TOKEN, threaded=False)
        admin_user = User.objects(username=cfg.admin_username).first()
        if not admin_user:
            return
        bot.send_message(
            admin_user.user_id,
            msg,
            parse_mode='html'
        )
    except:
        logger.exception('Error!')


_special_bot = TeleBot(BOT_TOKEN, threaded=False)


def smwae_check(chat_id, msg_text, user: User, parse_mode='html', reply_markup=None):
    try:
        _special_bot.send_message(
            chat_id or user.user_id,
            msg_text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        return True
    except ApiException as e:
        res = loads(e.result.text)
        if res['description'].find('was blocked') != -1:
            competitor: Competitor = user.check_association()
            if not competitor:
                # Some strange shit just happened here
                send_msg_to_admin(
                    get_translation_for('admin_notification_tg_user_blocked_and_competitor_vanished').format(user.str_repr())
                )
                return False
            competitor.change_status(COMPETITOR_STATUS.INACTIVE, bot=_special_bot, do_not_notify_admin=True)
            competitor.save()
            send_msg_to_admin(
                get_translation_for('admin_notification_tg_user_blocked').format(user.str_repr(), competitor.name)
            )
            return False
        else:
            raise e
