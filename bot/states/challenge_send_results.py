from . import RET, BaseState
from localization.translations import get_translation_for

from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from models import User

from models import Competitor, COMPETITOR_STATUS, Result, RESULT
from bot.bot_methods import check_wrapper, get_opponent_and_opponent_user, teardown_challenge, render_result, \
    smwae_check
from bot.keyboards import get_results_keyboard, get_result_confirmation_keyboard
from helpers import to_int
from logger_settings import logger
from config import STATES_HISTORY_LEN


class ChallengeSendResultsState(BaseState):

    def __init__(self):
        super().__init__()
        self._buttons = {
            'back_btn': self.back_button,
            'to_menu_btn': self.main_menu_btn,
            'results_clear_btn': self.clear_results,
            'result_competitor_win_btn': self.register_my_win,
            'result_opponent_win_btn': self.register_opponent_wins,
            'results_confirm_btn': self.confirm_result,
            'results_scores_confirm_btn': self.confirm_scores
        }

    def process_result(self, message: Message, user: User, bot: TeleBot, competitor: Competitor, final=False):
        opponent, opponent_user = get_opponent_and_opponent_user(competitor)
        if not opponent or not opponent_user:
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_confirm_cannot_find_opponent_msg' if not opponent else 'challenge_confirm_cannot_fin_opponents_user_msg'
            )

        res = user.check_result()
        if not res:
            res = Result(
                player_a=competitor,
                player_b=opponent,
                confirmged=False
            )
            res.save()
            user.current_result = res
            user.save()

        text = render_result(
            res,
            final
        )

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=self.__base_keyboard(confirmation_stage=final),
            parse_mode='html'
        )
        return RET.OK, None, None, None

    @check_wrapper
    def entry(self, message: Message, user: User, bot: TeleBot, competitor: Competitor = None):
        if competitor is None:
            competitor = user.check_association()
        if competitor.status not in (COMPETITOR_STATUS.CHALLENGE_STARTER, COMPETITOR_STATUS.CHALLENGE_RECEIVER):
            logger.error(f"User ({user.user_id}) - {competitor.name} entered ChallengeSendResultsState with incorrect competitor status {competitor.status}")
            return RET.GO_TO_STATE, 'MenuState', message, user
        opponent, opponent_user = get_opponent_and_opponent_user(competitor)
        if not opponent or not opponent_user:
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_confirm_cannot_find_opponent_msg' if not opponent else 'challenge_confirm_cannot_fin_opponents_user_msg'
            )
        if not user.check_result():
            res = Result(
                player_a=competitor,
                player_b=opponent,
                confirmed=False
            )
            res.save()
            user.current_result = res
            user.save()
        elif not user.check_result().sent:
            bot.send_message(
                user.user_id,
                get_translation_for('results_enter_results_msg')
            )
        else:
            bot.send_message(
                message.chat.id,
                get_translation_for('results_already_sent_msg')
            )
            return RET.GO_TO_STATE, 'MenuState', message, user
        return self.process_result(message, user, bot, competitor, final=user.check_result().result is not None)

    @check_wrapper
    def process_message(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        score = to_int(message.text, None)
        if score is None:
            return super().process_message(message, user, bot)

        res: Result = user.check_result()
        if res.result is not None:
            return RET.OK, None, None, None
        # TODO: checks
        if len(res.scores) > 10:

            bot.send_message(
                user.user_id,
                get_translation_for('results_maximum_scores_entered_msg'),
                reply_markup=self.__base_keyboard()
            )
            return RET.OK, None, None, None

        if score < 0 or score > 15:
            bot.send_message(
                user.user_id,
                get_translation_for('results_incorrect_score_msg'),
                reply_markup=self.__base_keyboard()
            )
            return RET.OK, None, None, None

        res.scores.append(score)
        res.save()
        return self.process_result(
            message,
            user,
            bot,
            competitor
        )

    def __base_keyboard(self, **kwargs):
        return get_results_keyboard(**kwargs)

    @check_wrapper
    def back_button(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        res: Result = user.check_result()
        if res.result is not None:
            res.result = None
            res.save()
        elif len(res.scores) > 0:
            res.scores.pop()
            res.save()
        else:
            return RET.GO_TO_STATE, 'MenuState', message, user
        return self.process_result(
            message,
            user,
            bot,
            competitor
        )

    @check_wrapper
    def clear_results(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        res: Result = user.check_result()
        res.scores = []
        res.result = None
        res.save()
        return self.process_result(
            message,
            user,
            bot,
            competitor
        )

    @check_wrapper
    def confirm_scores(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        res = user.check_result()
        if not len(res.scores) or len(res.scores)%2:
            bot.send_message(
                message.chat.id,
                get_translation_for('result_scores_count_must_be_odd_msg'),
                reply_markup=self.__base_keyboard()
            )
            return RET.OK, None, None, None
        return self.process_result(message, user, bot, competitor, True)

    @check_wrapper
    def confirm_result(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        res = user.check_result()
        if not len(res.scores) or len(res.scores)%2:
            bot.send_message(
                message.chat.id,
                get_translation_for('result_scores_count_must_be_odd_msg')
            )
            return RET.OK, None, None, None
        if res.result is None:
            bot.send_message(
                message.chat.id,
                get_translation_for('result_winner_must_be_specified_msg')
            )
            return RET.OK, None, None, None

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

        opponent.previous_challenge_status = opponent.status
        opponent.change_status(COMPETITOR_STATUS.CHALLENGE_NEED_RESULTS_CONFIRMATION)
        opponent.save()

        ores = opponent_user.check_result()
        if ores:
            ores.delete()
        opponent_user.current_result = res
        opponent_user.states.append('ChallengeConfirmResultsState')
        if len(opponent_user.states) > STATES_HISTORY_LEN:
            del opponent_user.states[0]
        opponent_user.save()

        res.sent = True
        res.save()

        if not smwae_check(
            opponent_user.user_id,
            get_translation_for('result_confirmation_msg') + '\n' + render_result(
                res,
                final=False
            ),
            opponent_user,
            reply_markup=get_result_confirmation_keyboard(),
        ):
            teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'error_bot_blocked_by_opponent_challenge_canceled_msg'
            )
            return RET.GO_TO_STATE, 'MenuState', message, user

        bot.send_message(
            message.chat.id,
            get_translation_for('results_sent_to_opponent_msg')
        )
        return RET.GO_TO_STATE, 'MenuState', message, user

    @check_wrapper
    def register_my_win(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        res = user.check_result()
        if res.player_a == competitor:
            res.result = RESULT.A_WINS
        elif res.player_b == competitor:
            res.result = RESULT.B_WINS
        else:
            logger.error(f'Competitor {competitor.name} record vanished from results record {str(res.id)}')
            return RET.GO_TO_STATE, 'MenuState', message, user
        res.save()
        return self.process_result(
            message,
            user,
            bot,
            competitor,
            True
        )

    @check_wrapper
    def register_opponent_wins(self, message: Message, user: User, bot: TeleBot, competitor: Competitor):
        res = user.check_result()
        opponent, opponent_user = get_opponent_and_opponent_user(competitor)
        if not opponent or not opponent_user:
            return teardown_challenge(
                competitor,
                message,
                user,
                bot,
                'challenge_confirm_cannot_find_opponent_msg' if not opponent else 'challenge_confirm_cannot_fin_opponents_user_msg'
            )
        if res.player_a == opponent:
            res.result = RESULT.A_WINS
        elif res.player_b == opponent:
            res.result = RESULT.B_WINS
        else:
            logger.error(f'Opponent {opponent.name} record vanished from results record {str(res.id)}')
            return RET.GO_TO_STATE, 'MenuState', message, user
        res.save()
        return self.process_result(
            message,
            user,
            bot,
            competitor,
            True
        )
