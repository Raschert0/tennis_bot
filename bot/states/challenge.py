from . import RET, BaseState
from localization.translations import get_translation_for

from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from models import User

from google_integration.sheets.users import UsersSheet
from google_integration.sheets.logs import LogsSheet
from google_integration.sheets.usage_guard import guard
from models import Competitor, COMPETITOR_STATUS
from logger_settings import logger
from bot.bot_methods import render_pagination, check_wrapper, send_msg_to_admin, smwae_check
from bot.keyboards import get_challenge_confirmation_keyboard
from bson.objectid import ObjectId
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from mongoengine.errors import ValidationError
from helpers import to_int
from werkzeug.exceptions import NotFound
from bot.settings_interface import get_config
from datetime import datetime
from pytz import timezone
from config import STATES_HISTORY_LEN


class ChallengeSendState(BaseState):

    @staticmethod
    def get_possible_levels(l):
        ret = []
        for _ in range(3):
            l -= 1
            if l >= 1:
                ret.append(l)
            else:
                break
        return ret

    def update_and_paginate(self, message: Message, user: User, bot: TeleBot, competitor: Competitor, page=1, update=False, updateText=False):
        if guard.get_allowed()[0] and guard.update_allowed()[0]:
            UsersSheet.update_model()
        possible_levels = ChallengeSendState.get_possible_levels(competitor.level)
        available_competitors = Competitor.objects(
            status__in=(
                COMPETITOR_STATUS.ACTIVE,
                COMPETITOR_STATUS.PASSIVE
            ),
            level__in=possible_levels,
            id__ne=competitor.latest_challenge_sent_to.id if competitor.latest_challenge_sent_to is not None else ObjectId(),
            associated_user_vanished__ne=True
        ).paginate(page=1, per_page=10)
        if not render_pagination(
            available_competitors,
            message,
            bot,
            get_translation_for('challenge_send_msg'),
            self.__base_keyboard,
            update=update,
            updateText=updateText
        ):
            bot.send_message(
                message.chat.id,
                get_translation_for('challenge_no_applicable_competitors_msg')
            )
            return False
        return True

    @check_wrapper
    def entry(self, message: Message, user: User, bot: TeleBot, competitor: Competitor = None):
        if not competitor:
            competitor = user.check_association()
        if not competitor:
            bot.send_message(
                message.chat.id,
                get_translation_for('competitor_record_vanished_msg')
            )
            return RET.GO_TO_STATE, 'AuthenticationState', message, user
        if not self.update_and_paginate(
            message,
            user,
            bot,
            competitor
        ):
            return RET.GO_TO_STATE, 'MenuState', message, user
        return RET.OK, None, None, None

    def process_callback(self, callback:CallbackQuery, user: User, bot: TeleBot):
        data = callback.data
        if data.find('challenge_to_') != 0:
            return RET.ANSWER_CALLBACK, None, callback, user
        data = data.replace('challenge_to_', '')

        competitor: Competitor = user.check_association()
        if not competitor:
            bot.send_message(
                callback.message.chat.id,
                get_translation_for('competitor_record_vanished_msg')
            )
            return RET.ANSWER_AND_GO_TO_STATE, 'AuthenticationState', callback, user

        if data.find('user=') == 0:
            ds = data.split('=')
            if len(ds) == 2:
                opponent_id = ds[1]
                try:
                    opponent = Competitor.objects(id=opponent_id).first()
                    if opponent is not None:
                        text = get_translation_for('challenge_send_confirm_msg').format(opponent.name)
                        text = f'<b>{text}</b>\n' \
                               f'{get_translation_for("info_status_str")}: {Competitor.status_code_to_str_dict[opponent.status]}\n' \
                               f'{get_translation_for("info_level_str")}: {opponent.level or get_translation_for("not_found_str")}\n' \
                               f'{get_translation_for("info_matches_str")}: {opponent.matches}\n' \
                               f'{get_translation_for("info_wins_str")}: {opponent.wins}\n' \
                               f'{get_translation_for("info_losses_str")}: {opponent.losses}\n' \
                               f'{get_translation_for("info_performance_str")}: {opponent.performance}'
                        update_failed = False
                        try:
                            bot.edit_message_text(
                                text,
                                callback.message.chat.id,
                                callback.message.message_id,
                                reply_markup=self.__confirmation_keyboard(id=opponent_id),
                                parse_mode='html'
                            )
                        except:
                            update_failed = True
                            logger.exception(
                                f'Exception occurred while updating keyboard for challenge sending. Chat: {callback.message.chat.id}')
                        if update_failed:
                            bot.send_message(
                                callback.message.chat.id,
                                text,
                                reply_markup=self.__confirmation_keyboard(id=opponent_id),
                                parse_mode='html'
                            )
                        return RET.ANSWER_CALLBACK, None, callback, user
                    else:
                        return RET.ANSWER_CALLBACK, get_translation_for(
                            'authentication_specified_competitor_not_found_clb'), callback, user
                except ValidationError:
                    logger.exception(f'Incorrect opponent_id: {opponent_id} from user with user_id: {user.user_id}')
        elif data.find('paginate=') == 0:
            ds = data.split('=')
            if len(ds) == 2:
                page = ds[1]
                page = to_int(page, 1)
                try:
                    available_competitors = Competitor.objects(
                        status__in=(
                            COMPETITOR_STATUS.ACTIVE,
                            COMPETITOR_STATUS.PASSIVE
                        ),
                        level__in=self.get_possible_levels(competitor.level),
                        id__ne=competitor.latest_challenge_sent_to.id if competitor.latest_challenge_sent_to is not None else ObjectId(),
                        associated_user_vanished__ne=True
                    ).paginate(
                        page=page,
                        per_page=10)
                except NotFound:
                    logger.exception(f'User {user.user_id} tried to switch to nonexistent page {page}')
                    available_competitors = Competitor.objects(
                        status__in=(
                            COMPETITOR_STATUS.ACTIVE,
                            COMPETITOR_STATUS.PASSIVE
                        ),
                        level__in=self.get_possible_levels(competitor.level),
                        id__ne=competitor.latest_challenge_sent_to.id if competitor.latest_challenge_sent_to is not None else ObjectId(),
                        associated_user_vanished__ne=True
                    ).paginate(page=1, per_page=10)
                if not render_pagination(
                        available_competitors,
                        callback.message,
                        bot,
                        get_translation_for('challenge_send_msg'),
                        self.__base_keyboard,
                        update=True
                ):
                    bot.send_message(
                        callback.message.chat.id,
                        get_translation_for('challenge_no_applicable_competitors_msg')
                    )
        elif data.find('none') == 0:
            return RET.ANSWER_CALLBACK, None, callback, user
        elif data.find('refresh') == 0:
            if guard.get_allowed()[0] and guard.update_allowed()[0]:
                UsersSheet.update_model()
            available_competitors = Competitor.objects(
                status__in=(
                    COMPETITOR_STATUS.ACTIVE,
                    COMPETITOR_STATUS.PASSIVE
                ),
                level__in=self.get_possible_levels(competitor.level),
                id__ne=competitor.latest_challenge_sent_to.id if competitor.latest_challenge_sent_to is not None else ObjectId(),
                associated_user_vanished__ne=True
            ).paginate(page=1, per_page=10)
            if not render_pagination(
                available_competitors,
                callback.message,
                bot,
                get_translation_for('challenge_send_msg'),
                self.__base_keyboard,
                update=True,
            ):
                bot.send_message(
                    callback.message.chat.id,
                    get_translation_for('challenge_no_applicable_competitors_msg')
                )
        elif data.find('confirm_send=') == 0:
            ds = data.split('=')
            if len(ds) == 2:
                opponent_id = ds[1]
                if competitor.latest_challenge_sent_to and opponent_id == str(competitor.latest_challenge_sent_to):
                    bot.send_message(
                        callback.message.chat.id,
                        get_translation_for('challenge_opponent_no_longer_available_msg')
                    )
                    return RET.ANSWER_AND_GO_TO_STATE, 'MenuState', callback, user
                try:
                    opponent: Competitor = Competitor.objects(status__in = (
                            COMPETITOR_STATUS.ACTIVE,
                            COMPETITOR_STATUS.PASSIVE
                        ),
                        level__in=self.get_possible_levels(competitor.level),
                        id=opponent_id,
                        associated_user_vanished__ne=True
                    ).first()
                    if opponent is None:
                        bot.send_message(
                            callback.message.chat.id,
                            get_translation_for('challenge_opponent_no_longer_available_msg')
                        )
                        return RET.ANSWER_AND_GO_TO_STATE, 'MenuState', callback, user
                    opponent_user: User = User.objects(associated_with=opponent).first()
                    if opponent_user is None:
                        bot.send_message(
                            callback.message.chat.id,
                            get_translation_for('challenge_cannot_send_message_to_opponent_msg')
                        )
                        send_msg_to_admin(
                            get_translation_for('admin_notification_tg_user_vanished').format(opponent.name)
                        )
                        opponent.associated_user_vanished = True
                        opponent.save()

                        return RET.ANSWER_AND_GO_TO_STATE, 'MenuState', callback, user

                    config = get_config()
                    if opponent.status == COMPETITOR_STATUS.ACTIVE:
                        if not smwae_check(
                            opponent_user.user_id,
                            get_translation_for('challenge_you_are_challenged_msg').format(
                                user.user_id,
                                competitor.name,
                                competitor.level,
                                config.time_to_accept_challenge
                            ),
                            opponent_user,
                            reply_markup=get_challenge_confirmation_keyboard(),
                            parse_mode='html'
                        ):
                            bot.send_message(
                                callback.message.chat.id,
                                get_translation_for('error_bot_blocked_by_opponent_challenge_canceled_msg'),
                                parse_mode='html'
                            )
                            return RET.ANSWER_AND_GO_TO_STATE, 'MenuState', callback, user
                        opponent_user.reload()
                        opponent_user.states.append('ChallengeReceivedState')
                        if len(opponent_user.states) > STATES_HISTORY_LEN:
                            del opponent_user.states[0]
                        opponent_user.save()
                    elif opponent.status == COMPETITOR_STATUS.PASSIVE:
                        if not smwae_check(
                            opponent_user.user_id,
                            get_translation_for('challenge_you_are_challenged_passive_msg').format(
                                user.user_id,
                                competitor.name,
                                competitor.level,
                                config.time_to_accept_challenge
                            ),
                            opponent_user,
                            reply_markup=get_challenge_confirmation_keyboard(),
                            parse_mode='html'
                        ):
                            bot.send_message(
                                callback.message.chat.id,
                                get_translation_for('error_bot_blocked_by_opponent_challenge_canceled_msg'),
                                parse_mode='html'
                            )
                            return RET.ANSWER_AND_GO_TO_STATE, 'MenuState', callback, user
                        opponent_user.reload()
                        opponent_user.states.append('ChallengeReceivedState')
                        if len(opponent_user.states) > STATES_HISTORY_LEN:
                            del opponent_user.states[0]
                        opponent_user.save()
                    else:
                        logger.error(f'Trying to send message to opponent with incorrect state: {opponent.name} {opponent.legacy_number}')
                        bot.send_message(
                            callback.message.chat.id,
                            get_translation_for('error_occurred_contact_administrator_msg'),
                            parse_mode='html'
                        )
                        return RET.ANSWER_AND_GO_TO_STATE, 'MenuState', callback, user

                    opponent.previous_status = opponent.status
                    opponent.change_status(COMPETITOR_STATUS.CHALLENGE_NEED_RESPONSE)
                    opponent.in_challenge_with = competitor
                    opponent.latest_challenge_received_at = datetime.now(tz=timezone('Europe/Kiev'))
                    opponent.save()

                    competitor.previous_status = competitor.status
                    competitor.change_status(COMPETITOR_STATUS.CHALLENGE_INITIATED)
                    competitor.in_challenge_with = opponent
                    competitor.latest_challenge_sent_to = opponent
                    competitor.save()

                    user.dismiss_confirmed = False
                    user.save()

                    bot.send_message(
                        callback.message.chat.id,
                        get_translation_for('challenge_sent_msg').format(opponent_user.user_id, opponent.name),
                        parse_mode='html'
                    )

                    LogsSheet.glog(
                        get_translation_for('gsheet_log_player_created_challenge_for_player').format(competitor.name, opponent.name)
                    )

                    return RET.ANSWER_AND_GO_TO_STATE, 'MenuState', callback, user

                except ValidationError:
                    logger.exception(f'Incorrect opponent_id: {opponent_id} from user with user_id: {user.user_id}')

        elif data.find('cancel_send') == 0:
            if not self.update_and_paginate(
                callback.message,
                user,
                bot,
                competitor,
                update=True,
                updateText=True
            ):
                bot.send_message(
                    callback.message.chat.id,
                    get_translation_for('challenge_no_applicable_competitors_msg')
                )
        elif data.find('back') == 0:
            return RET.ANSWER_AND_GO_TO_STATE, 'MenuState', callback, user
        return RET.ANSWER_CALLBACK, None, callback, user

    def __base_keyboard(self, **kwargs):
        keyboard = InlineKeyboardMarkup(row_width=1)
        for name, id_ in kwargs.get('names', []):
            keyboard.add(InlineKeyboardButton(
                name,
                callback_data=f'challenge_to_user={id_}'
            ))
        if kwargs.get('has_pages', None) and kwargs.get('cur_page', None):
            end_row = [InlineKeyboardButton(
                '<',
                callback_data=f'challenge_to_paginate={kwargs["cur_page"] - 1}' if kwargs.get('has_prev', None) else 'challenge_to_none'
            ), InlineKeyboardButton(
                f'{kwargs["cur_page"]}{(" / " + str(kwargs["pages"]) if kwargs.get("pages", None) else "")}',
                callback_data='challenge_to_none'
            ), InlineKeyboardButton(
                '>',
                callback_data=f'challenge_to_paginate={kwargs["cur_page"] + 1}' if kwargs.get('has_next', None) else 'challenge_to_none'
            )]
            keyboard.row(*end_row)
        keyboard.row(
            InlineKeyboardButton(
                get_translation_for('back_btn'),
                callback_data='challenge_to_back'
            ),
            InlineKeyboardButton(
                '🔄',
                callback_data='challenge_to_refresh'
            )
        )
        return keyboard

    def __confirmation_keyboard(self, id):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton(get_translation_for('challenge_send_confirm_yes_btn'),
                                 callback_data=f'challenge_to_confirm_send={id}'),
            InlineKeyboardButton(get_translation_for('challenge_send_confirm_no_btn'),
                                 callback_data=f'challenge_to_cancel_send')
        )
        return keyboard
