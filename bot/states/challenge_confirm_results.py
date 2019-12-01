from . import RET, BaseState
from localization.translations import get_translation_for

from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from models import User

from models import Competitor, COMPETITOR_STATUS, Result, RESULT
from bot.keyboards import get_result_confirmation_keyboard, get_menu_keyboard
from bot.bot_methods import check_wrapper, get_opponent_and_opponent_user, teardown_challenge, render_result
from logger_settings import logger
from config import STATES_HISTORY_LEN
from datetime import datetime
from pytz import timezone


class ChallengeConfirmResultsState(BaseState):

    def __init__(self):
        super().__init__()
        self._buttons = {
            'back_btn': self.main_menu_btn,
            'result_confirmation_confirm_btn': self.confirm_results,
            'result_confirmation_dismiss_btn': self.dismiss_results,
        }

    @check_wrapper
    def entry(self, message: Message, user: User, bot: TeleBot, competitor: Competitor = None):
        if competitor is None:
            competitor = user.check_association()
        res = user.check_result()
        if not res:
            pass
            # TODO
        opponent, opponent_user = get_opponent_and_opponent_user(competitor)
        if not opponent or not opponent_user:
            res.delete()
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_confirm_cannot_find_opponent_msg' if not opponent else 'challenge_confirm_cannot_fin_opponents_user_msg'
            )

        bot.send_message(
            message.chat.id,
            get_translation_for('result_confirmation_msg') + '\n' + render_result(
                res,
                final=False
            ),
            reply_markup=get_result_confirmation_keyboard()
        )
        return RET.OK, None, None, None

    def __base_keyboard(self, **kwargs):
        return get_result_confirmation_keyboard(**kwargs)

    @check_wrapper
    def confirm_results(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        res = user.check_result()
        if not res:
            pass
            # TODO
        opponent, opponent_user = get_opponent_and_opponent_user(competitor)
        if not opponent or not opponent_user:
            res.delete()
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_confirm_cannot_find_opponent_msg' if not opponent else 'challenge_confirm_cannot_fin_opponents_user_msg'
            )

        if not user.dismiss_confirmed:
            bot.send_message(
                message.chat.id,
                get_translation_for('result_confirmation_confirm_msg')
            )
            user.dismiss_confirmed = True
            user.save()
            return RET.OK, None, None, None
        else:
            user.dismiss_confirmed = False
            user.save()

        pa = res.player_a.fetch()
        pb = res.player_b.fetch()
        winner: Competitor
        loser: Competitor
        if res.result == RESULT.A_WINS:
            winner = pa
            loser = pb
        elif res.result == RESULT.B_WINS:
            winner = pb
            loser = pa
        else:
            logger.error('INCONSISTENT RESULT OF A RESULT')
            return RET.GO_TO_STATE, 'MenuState', None, None

        res.confirmed = True
        res.date = datetime.now(timezone('Europe/Kiev'))
        res.player_a_s = pa.name
        res.player_b_s = pb.name
        res.save()

        winner.wins = winner.wins + 1 if winner.wins is not None else 1
        winner.matches = winner.matches + 1 if winner.matches is not None else 1
        winner.status = COMPETITOR_STATUS.ACTIVE
        winner.previous_status = None
        winner.previous_challenge_status = None
        winner.challenge_started_at = None
        winner.in_challenge_with = None
        winner.save()

        loser.wins = loser.wins + 1 if loser.wins is not None else 1
        loser.matches = loser.matches + 1 if loser.matches is not None else 1
        loser.status = loser.previous_status
        loser.previous_status = None
        loser.previous_challenge_status = None
        loser.challenge_started_at = None
        loser.in_challenge_with = None
        loser.save()

        prev_level, new_level = None, None
        if winner.level > loser.level:
            prev_level = winner.level
            new_level = loser.level

        if prev_level:
            if opponent == winner:
                bot.send_message(
                    opponent_user.user_id,
                    get_translation_for('result_confirmation_confirmed_opponent_msg') + '\n' +
                    get_translation_for('your_level_changed_str').format(prev_level, new_level),
                    reply_markup=get_menu_keyboard(status=opponent.status)
                )
                bot.send_message(
                    message.chat.id,
                    get_translation_for('result_confirmation_confirmed_msg') + '\n' +
                    get_translation_for('your_level_changed_str').format(new_level, prev_level),
                )
                opponent.reload()
                opponent.level = new_level
                opponent.save()
                competitor.reload()
                competitor.level = prev_level
                competitor.save()
            else:
                bot.send_message(
                    opponent_user.user_id,
                    get_translation_for('result_confirmation_confirmed_opponent_msg') + '\n' +
                    get_translation_for('your_level_changed_str').format(new_level, new_level),
                    reply_markup=get_menu_keyboard(status=opponent.status)
                )
                bot.send_message(
                    message.chat.id,
                    get_translation_for('result_confirmation_confirmed_msg') + '\n' +
                    get_translation_for('your_level_changed_str').format(prev_level, new_level),
                )
                competitor.reload()
                competitor.level = new_level
                competitor.save()
                opponent.reload()
                opponent.level = prev_level
                opponent.save()
        else:
            bot.send_message(
                opponent_user.user_id,
                get_translation_for('result_confirmation_confirmed_opponent_msg'),
                reply_markup=get_menu_keyboard(status=opponent.status)
            )

        opponent_user.reload()
        opponent_user.current_result = None
        opponent_user.states.append('MenuState')
        if len(opponent_user.states) > STATES_HISTORY_LEN:
            del opponent_user.states[0]
        opponent_user.save()

        user.reload()
        user.current_result = None
        user.save()

        return RET.GO_TO_STATE, 'MenuState', message, user

    @check_wrapper
    def dismiss_results(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        res = user.check_result()
        if not res:
            pass
            # TODO
        opponent, opponent_user = get_opponent_and_opponent_user(competitor)
        if not opponent or not opponent_user:
            res.delete()
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_confirm_cannot_find_opponent_msg' if not opponent else 'challenge_confirm_cannot_fin_opponents_user_msg'
            )

        opponent.status = opponent.previous_challenge_status
        opponent.previous_challenge_status = None
        opponent.save()

        competitor.status = competitor.previous_challenge_status
        competitor.previous_challenge_status = None
        competitor.save()

        bot.send_message(
            opponent_user.user_id,
            get_translation_for('result_confirmation_dismissed_opponent_msg'),
            reply_markup=get_menu_keyboard(status=opponent.status)
        )

        bot.send_message(
            message.chat.id,
            get_translation_for('result_confirmation_dismissed_msg')
        )

        user.current_result = None
        user.save()
        return RET.GO_TO_STATE, 'MenuState', None, None
