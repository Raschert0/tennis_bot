from typing import Optional, Any

from . import RET, BaseState
from localization.translations import get_translation_for

from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from models import User

from models import Competitor, COMPETITOR_STATUS, Result, RESULT
from bot.keyboards import get_challenge_confirmation_keyboard, get_menu_keyboard
from bot.bot_methods import check_wrapper, get_opponent_and_opponent_user, teardown_challenge, smwae_check
from bot.settings_interface import get_config
from datetime import datetime
from pytz import timezone
from config import STATES_HISTORY_LEN
from google_integration.sheets.matches import ResultsSheet
from google_integration.sheets.logs import LogsSheet
from google_integration.sheets.users import UsersSheet
from logger_settings import logger


class ChallengeReceivedState(BaseState):

    def __init__(self):
        super().__init__()
        self._buttons = {
            'challenge_received_accept_btn': self.accept_button,
            'challenge_received_dismiss_btn': self.dismiss_button,
            'back_btn': self.back_button
        }

    def form_message(self, competitor: Competitor, opponent: Competitor, opponent_user: User):
        text = f'<b>{get_translation_for("challenge_received_status")}:</b> <a href="tg://user?id={opponent_user.user_id}">{opponent.name}</a>. <b>{get_translation_for("info_level_str")}: {opponent.level}</b>'
        if competitor.previous_status == COMPETITOR_STATUS.PASSIVE:
            text = f'{text}\n' \
                   f'{get_translation_for("challenge_received_warning")}'
        return text

    @check_wrapper
    def entry(self, message: Message, user: User, bot: TeleBot, competitor: Competitor = None):
        if not competitor:
            competitor = user.check_association()
        if competitor.status != COMPETITOR_STATUS.CHALLENGE_NEED_RESPONSE:
            bot.send_message(
                message.chat.id,
                get_translation_for('challenge_received_not_found')
            )
            return RET.GO_TO_STATE, 'MenuState', message, user
        opponent = competitor.in_challenge_with.fetch()
        opponent_user = User.objects(associated_with=opponent).first()
        bot.send_message(
            message.chat.id,
            self.form_message(competitor, opponent, opponent_user),
            reply_markup=self.__base_keyboard(),
            parse_mode='html'
        )

        user.dismiss_confirmed = False
        user.save()
        return RET.OK, None, None, None

    @check_wrapper
    def process_message(self, message: Message, user: User, bot: TeleBot, competitor: Competitor = None):
        if not competitor:
            competitor = user.check_association()
        if competitor.status != COMPETITOR_STATUS.CHALLENGE_NEED_RESPONSE:
            bot.send_message(
                message.chat.id,
                get_translation_for('challenge_received_not_found')
            )
            return RET.GO_TO_STATE, 'MenuState', message, user

    def __base_keyboard(self, **kwargs):
        return get_challenge_confirmation_keyboard(**kwargs)

    #Buttons

    def back_button(self, message: Message, user: User, bot: TeleBot):
        return RET.GO_TO_STATE, 'MenuState', message, user

    @check_wrapper
    def accept_button(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        opponent_user: User
        opponent, opponent_user = get_opponent_and_opponent_user(competitor)
        if not opponent or not opponent_user:
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_confirm_cannot_find_opponent_msg' if not opponent else 'challenge_confirm_cannot_fin_opponents_user_msg'
            )

        opponent.change_status(COMPETITOR_STATUS.CHALLENGE_STARTER)
        competitor.change_status(COMPETITOR_STATUS.CHALLENGE_RECEIVER)
        competitor.latest_challenge_received_at = None

        n = datetime.now(tz=timezone('Europe/Kiev'))
        opponent.challenge_started_at = n
        competitor.challenge_started_at = n

        competitor.challenges_dismissed_in_a_row = 0

        opponent.save()
        competitor.save()

        config = get_config()
        if not smwae_check(
            opponent_user.user_id,
            get_translation_for('challenge_confirm_challenge_accepted_opponent_msg').format(
                f'<a href="tg://user?id={user.user_id}">{competitor.name}</a>',
                config.time_to_play_challenge
            ),
            opponent_user,
            reply_markup=get_menu_keyboard(status=opponent.status),
            parse_mode='html'
        ):
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'error_bot_blocked_by_opponent_challenge_canceled_msg'
            )
        opponent_user.reload()
        opponent_user.dismiss_confirmed = False
        opponent_user.states.append('MenuState')
        if len(opponent_user.states) > STATES_HISTORY_LEN:
            del opponent_user.states[0]
        opponent_user.save()

        user.dismiss_confirmed = False
        user.save()
        bot.send_message(
            user.user_id,
            get_translation_for('challenge_confirm_challenge_accepted_competitor_msg').format(
                f'<a href="tg://user?id={opponent_user.user_id}">{opponent.name}</a>',  # TODO
                config.time_to_play_challenge
            ),
            parse_mode='html'
        )

        LogsSheet.glog(
            get_translation_for('gsheet_log_player_accepted_challenge_from_player').format(competitor.name, opponent.name)
        )

        return RET.GO_TO_STATE, 'MenuState', message, user

    @check_wrapper
    def dismiss_button(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        defeat = False
        if not user.dismiss_confirmed:
            if competitor.previous_status == COMPETITOR_STATUS.PASSIVE:
                bot.send_message(
                    message.chat.id,
                    get_translation_for('challenge_confirm_technical_defeat')
                )
            else:
                bot.send_message(
                    message.chat.id,
                    get_translation_for('challenge_received_dismiss_confirm_msg')
                )
            user.dismiss_confirmed = True
            user.save()
            return RET.OK, None, None, None
        else:
            user.dismiss_confirmed = False
            user.save()
            if competitor.previous_status == COMPETITOR_STATUS.PASSIVE and competitor.challenges_dismissed_in_a_row >= 1:
                defeat = True

        opponent, opponent_user = get_opponent_and_opponent_user(competitor)
        if not opponent or not opponent_user:
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_confirm_cannot_find_opponent_msg' if not opponent else 'challenge_confirm_cannot_fin_opponents_user_msg'
            )

        opponent.in_challenge_with = None
        opponent.change_status(opponent.previous_status)
        opponent.previous_status = None

        if defeat:
            opponent.wins = opponent.wins + 1 if opponent.wins is not None else 1
            opponent.matches = opponent.matches + 1 if opponent.matches is not None else 1
            level_change = None
            if opponent.level > competitor.level:
                level_change = f'{opponent.level}->{competitor.level}'
                c = opponent.level
                opponent.level = competitor.level
                competitor.level = c
                ResultsSheet.upload_canceled_result(opponent, competitor, level_change, was_dismissed=True)
            UsersSheet.update_competitor_table_record(opponent)
            res = Result(
                player_a=opponent,
                player_a_s=opponent.name,
                player_b=competitor,
                player_b_s=competitor.name,
                result=RESULT.DISMISSED,
                canceled=True,
                date=datetime.now(tz=timezone('Europe/Kiev')),
                level_change=level_change
            )
            res.save()

            config = get_config()
            if config.group_chat_id:
                gmsg = get_translation_for('group_chat_technical_win_report_msg').format(opponent.name, competitor.name)
                if level_change:
                    gmsg += '.\n'
                    gmsg += get_translation_for('group_chat_players_level_changed').format(level_change)

                try:
                    bot.send_message(
                        config.group_chat_id,
                        gmsg,
                        parse_mode='html'
                    )
                except:
                    logger.exception('Exception occurred while sending message to group chat')

            result = Result(
                player_a=opponent,
                player_b=competitor,
                result=RESULT.A_WINS
            )
            result.save()

        opponent.save()

        competitor.in_challenge_with = None
        if defeat:
            competitor.change_status(COMPETITOR_STATUS.ACTIVE)
            competitor.challenges_dismissed_in_a_row = 0
            competitor.losses += competitor.losses + 1 if competitor.losses is not None else 1
            competitor.matches += competitor.matches + 1 if competitor.matches is not None else 1
            UsersSheet.update_competitor_table_record(competitor)
        else:
            competitor.change_status(COMPETITOR_STATUS.PASSIVE)
            competitor.challenges_dismissed_in_a_row = 1
        competitor.challenges_dismissed_total = competitor.challenges_dismissed_total + 1 if competitor.challenges_dismissed_total is not None else 1
        competitor.latest_challenge_received_at = None
        competitor.save()

        opponent_user.states.append('MenuState')
        if len(opponent_user.states) > STATES_HISTORY_LEN:
            del opponent_user.states[0]
        opponent_user.save()

        if defeat:
            smwae_check(
                opponent_user.user_id,
                get_translation_for('challenge_confirm_opponent_wins') + ' ' + str(opponent.level),
                opponent_user,
                reply_markup=get_menu_keyboard(status=opponent.status)
            )
            bot.send_message(
                user.user_id,
                get_translation_for('challenge_confirm_competitor_losses') + ' ' + str(competitor.level),
            )
        else:
            smwae_check(
                opponent_user.user_id,
                get_translation_for('challenge_confirmation_dismissed_opponent_msg'),
                opponent_user,
                reply_markup=get_menu_keyboard(status=opponent.status)
            )
            bot.send_message(
                user.user_id,
                get_translation_for('challenge_confirmation_dismissed_competitor_msg'),
            )

        LogsSheet.glog(
            get_translation_for('gsheet_log_player_dismissed_challenge_from_player').format(competitor.name, opponent.name)
        )

        return RET.GO_TO_STATE, 'MenuState', message, user
