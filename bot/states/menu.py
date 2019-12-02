from . import RET, BaseState
from localization.translations import get_translation_for

from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from models import User

from models import Competitor, COMPETITOR_STATUS
from logger_settings import logger
from bot.bot_methods import check_wrapper, get_opponent_and_opponent_user, teardown_challenge
from bot.settings_interface import get_config
from bot.keyboards import get_menu_keyboard
from google_integration.sheets.users import UsersSheet
from datetime import datetime, timedelta
from pytz import timezone
from helpers import mongo_time_to_local


class MenuState(BaseState):

    def __init__(self):
        super().__init__()
        self._buttons = {
            'menu_info_btn': self.info_btn,
            'menu_go_on_vacation_btn': self.go_on_vacation,
            'menu_go_on_sick_leave_btn': self.go_on_sick_leave,
            'menu_end_vacation_btn': self.end_vacation,
            'menu_end_sick_leave_btn': self.end_sick_leave,
            'menu_reply_to_challenge_request_btn': self.reply_on_challenge,
            'menu_cancel_challenge_request_btn': self.cancel_challenge_request,
            'menu_submit_challenge_results_btn': self.submit_results,
            'challenge_cancel_request_opponent_confirm_btn': self.confirm_cancellation_opponent,
            'challenge_cancel_request_opponent_dismiss_btn': self.dismiss_cancellation_opponent,
            'menu_accept_challenge_results_btn': self.accept_results,
            'menu_create_challenge_btn': self.create_challenge,
            'menu_cancel_challenge_btn': self.cancel_challenge,
        }

    @check_wrapper
    def entry(self, message: Message, user: User, bot: TeleBot, competitor=None):
        if not competitor:
            logger.warning('Check_wrapper not provided Competitor object')
            competitor = user.associated_with.fetch()
        bot.send_message(
            message.chat.id,
            get_translation_for('menu_msg'),
            reply_markup=self.__base_keyboard(status=competitor.status)
        )
        return RET.OK, None, None, None

    def __base_keyboard(self, **kwargs):
        return get_menu_keyboard(**kwargs)

    # Buttons

    @check_wrapper
    def info_btn(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        config = get_config()
        info = f'<b>{competitor.name}</b>\n' \
               f'{get_translation_for("info_status_str")}: {Competitor.status_code_to_str_dict[competitor.status]}\n' \
               f'{get_translation_for("info_level_str")}: {competitor.level or get_translation_for("not_found_str")}\n' \
               f'{get_translation_for("info_matches_str")}: {competitor.matches}\n' \
               f'{get_translation_for("info_wins_str")}: {competitor.wins}\n' \
               f'{get_translation_for("info_losses_str")}: {competitor.losses}\n' \
               f'{get_translation_for("info_performance_str")}: {competitor.performance}\n' \
               f'{get_translation_for("vacation_days_used_str")}: {timedelta(seconds=competitor.used_vacation_time).days if competitor.used_vacation_time else 0}/{config.vacation_time}'
        bot.send_message(
            message.chat.id,
            info,
            reply_markup=self.__base_keyboard(status=competitor.status),
            parse_mode='html'
        )
        return RET.OK, None, None, None

    @check_wrapper
    def go_on_vacation(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        if competitor.status not in (COMPETITOR_STATUS.ACTIVE, COMPETITOR_STATUS.PASSIVE):
            return RET.OK, None, None, None
        config = get_config()
        if timedelta(seconds=competitor.used_vacation_time).days >= config.vacation_time:
            bot.send_message(
                message.chat.id,
                get_translation_for('menu_vacation_no_days_left_msg'),
                reply_markup=self.__base_keyboard(status=competitor.status)
            )
            return RET.OK, None, None, None
        competitor.previous_status = competitor.status
        competitor.status = COMPETITOR_STATUS.VACATION
        competitor.vacation_started_at = datetime.now(tz=timezone('Europe/Kiev'))
        competitor.save()
        bot.send_message(
            message.chat.id,
            get_translation_for('menu_on_vacation_start_msg'),
            reply_markup=self.__base_keyboard(status=competitor.status)
        )
        UsersSheet.update_competitor_status(competitor)
        return RET.OK, None, None, None

    @check_wrapper
    def go_on_sick_leave(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        if competitor.status not in (COMPETITOR_STATUS.ACTIVE, COMPETITOR_STATUS.PASSIVE):
            return RET.OK, None, None, None
        competitor.previous_status = competitor.status
        competitor.status = COMPETITOR_STATUS.INJUIRY
        competitor.save()
        bot.send_message(
            message.chat.id,
            get_translation_for('menu_on_sick_leave_start_msg'),
            reply_markup=self.__base_keyboard(status=competitor.status)
        )
        UsersSheet.update_competitor_status(competitor)
        return RET.OK, None, None, None

    @check_wrapper
    def end_vacation(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        if competitor.status != COMPETITOR_STATUS.VACATION:
            return RET.OK, None, None, None
        if not competitor.vacation_started_at:
            logger.error(f"Cannot calculate user's ({user.user_id}) time on vacation - cannot find vacation_started_at")
            delta = 0
        else:
            tz = timezone('Europe/Kiev')
            now = datetime.now(tz=tz)
            delta = now - mongo_time_to_local(competitor.vacation_started_at, tz)
            delta = delta.total_seconds()
        if competitor.used_vacation_time is None:
            competitor.used_vacation_time = delta
        else:
            competitor.used_vacation_time += delta
        competitor.status = competitor.previous_status
        competitor.save()
        bot.send_message(
            message.chat.id,
            get_translation_for('menu_on_vacation_end_manual_msg'),
            reply_markup=self.__base_keyboard(status=competitor.status)
        )
        UsersSheet.update_competitor_status(competitor)
        return RET.OK, None, None, None

    @check_wrapper
    def end_sick_leave(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        if competitor.status != COMPETITOR_STATUS.INJUIRY:
            return RET.OK, None, None, None
        competitor.status = competitor.previous_status
        competitor.save()
        bot.send_message(
            message.chat.id,
            get_translation_for('menu_on_sick_leave_end_msg'),
            reply_markup=self.__base_keyboard(status=competitor.status)
        )
        UsersSheet.update_competitor_status(competitor)
        return RET.OK, None, None, None

    @check_wrapper
    def reply_on_challenge(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        if competitor.status != COMPETITOR_STATUS.CHALLENGE_NEED_RESPONSE:
            return RET.OK, None, None, None
        return RET.GO_TO_STATE, 'ChallengeReceivedState', message, user

    @check_wrapper
    def cancel_challenge_request(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        if competitor.status != COMPETITOR_STATUS.CHALLENGE_INITIATED:
            return RET.OK, None, None, None
        if not user.dismiss_confirmed:
            bot.send_message(
                message.chat.id,
                get_translation_for('challenge_request_cancel_confirm_msg'),
                reply_markup=self.__base_keyboard(status=competitor.status)
            )
            user.dismiss_confirmed = True
            user.save()
            return RET.OK, None, None, None
        else:
            user.dismiss_confirmed = False
            user.save()

        opponent, opponent_user = get_opponent_and_opponent_user(competitor)
        if not opponent or not opponent_user:
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_request_canceled_to_competitor_msg',
                canceled_by_bot=False
            )
        else:
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_request_canceled_to_competitor_msg',
                canceled_by_bot=False,
                opponent=opponent,
                opponent_msg_key='challenge_request_canceled_to_opponent_msg'
            )

    @check_wrapper
    def submit_results(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        if competitor.status not in (COMPETITOR_STATUS.CHALLENGE_STARTER, COMPETITOR_STATUS.CHALLENGE_RECEIVER):
            return RET.OK, None, None, None
        opponent, opponent_user = get_opponent_and_opponent_user(competitor)
        if not opponent or not opponent_user:
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_confirm_cannot_find_opponent_msg' if not opponent else 'challenge_confirm_cannot_fin_opponents_user_msg'
            )
        if opponent.status == COMPETITOR_STATUS.CHALLENGE_NEED_RESULTS_CONFIRMATION:
            bot.send_message(
                message.chat.id,
                get_translation_for('results_already_sent_msg')
            )
            return RET.OK, None, None, None
        return RET.GO_TO_STATE, 'ChallengeSendResultsState', message, user

    @check_wrapper
    def cancel_challenge(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        if competitor.status != COMPETITOR_STATUS.CHALLENGE_STARTER:
            return RET.OK, None, None, None
        opponent, opponent_user = get_opponent_and_opponent_user(competitor)
        if not opponent or not opponent_user:
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_confirm_cannot_find_opponent_msg' if not opponent else 'challenge_confirm_cannot_fin_opponents_user_msg'
            )

        if opponent.status == COMPETITOR_STATUS.CHALLENGE_NEED_CANCELLATION_CONFIRMATION:
            bot.send_message(
                user.user_id,
                get_translation_for('challenge_cancellation_in_progress_msg').format(opponent.name),
                reply_markup=self.__base_keyboard(status=competitor.status)
            )
            return RET.OK, None, None, None
        if opponent.status == COMPETITOR_STATUS.CHALLENGE_NEED_RESULTS_CONFIRMATION:
            bot.send_message(
                user.user_id,
                get_translation_for('challenge_cancellation_opponent_is_verifying_results_msg').format(opponent.name),
                reply_markup=self.__base_keyboard(status=competitor.status)
            )
            return RET.OK, None, None, None

        if not user.dismiss_confirmed:
            bot.send_message(
                message.chat.id,
                get_translation_for('challenge_cancel_msg'),
                reply_markup=self.__base_keyboard(status=competitor.status)
            )
            user.dismiss_confirmed = True
            user.save()
            return RET.OK, None, None, None
        else:
            user.dismiss_confirmed = False
            user.save()

        opponent.previous_challenge_status = opponent.status
        opponent.status = COMPETITOR_STATUS.CHALLENGE_NEED_CANCELLATION_CONFIRMATION
        opponent.save()

        opponent_user.dismiss_confirmed = False
        opponent_user.save()

        bot.send_message(
            opponent_user.user_id,
            get_translation_for('challenge_cancel_request_opponent_msg').format(competitor.name),
            reply_markup=self.__base_keyboard(status=opponent.status)
        )

        bot.send_message(
            message.chat.id,
            get_translation_for('challenge_cancel_request_sent_msg'),
            reply_markup=self.__base_keyboard(status=competitor.status)
        )
        return RET.OK, None, None, None

    @check_wrapper
    def confirm_cancellation_opponent(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        if competitor.status != COMPETITOR_STATUS.CHALLENGE_NEED_CANCELLATION_CONFIRMATION:
            return RET.OK, None, None, None
        if not user.dismiss_confirmed:
            bot.send_message(
                message.chat.id,
                get_translation_for('challenge_cancel_msg'),
                reply_markup=self.__base_keyboard(status=competitor.status)
            )
            user.dismiss_confirmed = True
            user.save()
            return RET.OK, None, None, None
        else:
            user.dismiss_confirmed = False
            user.save()

        opponent, opponent_user = get_opponent_and_opponent_user(competitor)
        if not opponent or not opponent_user:
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_confirm_cannot_find_opponent_msg' if not opponent else 'challenge_confirm_cannot_fin_opponents_user_msg'
            )

        opponent.status = opponent.previous_status
        opponent.previous_status = None
        opponent.previous_challenge_status = None
        opponent.in_challenge_with = None
        opponent.challenge_started_at = None
        opponent.save()

        competitor.status = competitor.previous_status
        competitor.previous_status = None
        competitor.previous_challenge_status = None
        competitor.in_challenge_with = None
        competitor.challenge_started_at = None
        competitor.save()

        bot.send_message(
            opponent_user.user_id,
            get_translation_for('challenge_canceled_msg').format(competitor.name),
            reply_markup=self.__base_keyboard(status=opponent.status)
        )

        bot.send_message(
            message.chat.id,
            get_translation_for('challenge_canceled_msg').format(opponent.name),
            reply_markup=self.__base_keyboard(status=competitor.status)
        )
        return RET.OK, None, None, None

    @check_wrapper
    def dismiss_cancellation_opponent(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        if competitor.status != COMPETITOR_STATUS.CHALLENGE_NEED_CANCELLATION_CONFIRMATION:
            return RET.OK, None, None, None

        opponent, opponent_user = get_opponent_and_opponent_user(competitor)
        if not opponent or not opponent_user:
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_confirm_cannot_find_opponent_msg' if not opponent else 'challenge_confirm_cannot_fin_opponents_user_msg'
            )

        competitor.status = competitor.previous_challenge_status
        competitor.previous_challenge_status = None
        competitor.save()

        user.dismiss_confirmed = False
        user.save()

        bot.send_message(
            opponent_user.user_id,
            get_translation_for('challenge_cancellation_denied_opponent_msg').format(competitor.name),
            reply_markup=self.__base_keyboard(status=opponent.status)
        )

        bot.send_message(
            user.user_id,
            get_translation_for('challenge_cancellation_denied_msg').format(opponent.name),
            reply_markup=self.__base_keyboard(status=competitor.status)
        )
        return RET.OK, None, None, None

    @check_wrapper
    def accept_results(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        if competitor.status != COMPETITOR_STATUS.CHALLENGE_NEED_RESULTS_CONFIRMATION:
            return RET.OK, None, None, None
        return RET.GO_TO_STATE, 'ChallengeConfirmResultsState', message, user

    @check_wrapper
    def create_challenge(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        if competitor.status not in (COMPETITOR_STATUS.ACTIVE, COMPETITOR_STATUS.PASSIVE):
            return RET.OK, None, None, None
        return RET.GO_TO_STATE, 'ChallengeSendState', message, user
