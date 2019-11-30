from . import RET, BaseState
from localization.translations import get_translation_for

from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from models import User

from telebot.types import ReplyKeyboardMarkup
from models import Competitor, COMPETITOR_STATUS
from logger_settings import logger
from bot.bot_methods import competitor_check
from google_integration.sheets.users import UsersSheet


class MenuState(BaseState):

    def __init__(self):
        super().__init__()
        self._buttons = {
            'menu_info_btn': self.info_btn,
        }

    def entry(self, message: Message, user: User, bot: TeleBot):
        ch = competitor_check(message, user, bot)
        if not ch[0]:
            return ch[1]
        competitor = user.associated_with.fetch()
        bot.send_message(
            message.chat.id,
            get_translation_for('menu_msg'),
            reply_markup=self.__base_keyboard(status=competitor.status)
        )
        return RET.OK, None, None, None

    def __base_keyboard(self, **kwargs):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

        status = kwargs.get('status', COMPETITOR_STATUS.UNATHORIZED)
        if status == COMPETITOR_STATUS.UNATHORIZED:
            logger.error('Not provided status for keyboard in menu state. Backing up ACTIVE state')
            status = COMPETITOR_STATUS.ACTIVE

        if status in (COMPETITOR_STATUS.ACTIVE, COMPETITOR_STATUS.PASSIVE):
            keyboard.row(get_translation_for('menu_info_btn'))
            keyboard.row(get_translation_for('menu_create_challenge_btn'))
            keyboard.row(get_translation_for('menu_go_to_vacation_btn'))
            keyboard.row(get_translation_for('menu_got_to_injuiry_btn'))
        elif status == COMPETITOR_STATUS.CHALLENGE_INITIATED:
            keyboard.row(get_translation_for('menu_info_btn'))
            keyboard.row(get_translation_for('menu_cancel_challenge_request_btn'))
        elif status == COMPETITOR_STATUS.CHALLENGE_NEED_RESPONSE:
            keyboard.row(get_translation_for('menu_info_btn'))
            keyboard.row(get_translation_for('menu_reply_to_challenge_request_btn'))
        elif status == COMPETITOR_STATUS.CHALLENGE:
            keyboard.row(get_translation_for('menu_info_btn'))
            keyboard.row(get_translation_for('menu_submit_challenge_results_btn'))
            keyboard.row(get_translation_for('menu_cancel_challenge_btn'))
        elif status == COMPETITOR_STATUS.VACATION:
            keyboard.row(get_translation_for('menu_info_btn'))
            keyboard.row(get_translation_for('menu_end_vacation_btn'))
        elif status == COMPETITOR_STATUS.INJUIRY:
            keyboard.row(get_translation_for('menu_info_btn'))
            keyboard.row(get_translation_for('menu_end_injuiry_status_btn'))
        return keyboard

    # Buttons

    def info_btn(self, message: Message, user: User, bot: TeleBot):
        ch = competitor_check(message, user, bot)
        if not ch[0]:
            return ch[1]
        competitor = user.associated_with.fetch()
        info = f'<b>{competitor.name}</b>\n' \
               f'{get_translation_for("info_status_str")}: {UsersSheet.status_code_to_str_dict[competitor.status]}\n' \
               f'{get_translation_for("info_matches_str")}: {competitor.matches}\n' \
               f'{get_translation_for("info_wins_str")}: {competitor.wins}\n' \
               f'{get_translation_for("info_losses_str")}: {competitor.losses}\n' \
               f'{get_translation_for("info_performance_str")}: {competitor.performance}\n'
        bot.send_message(
            message.chat.id,
            info,
            reply_markup=self.__base_keyboard(status=competitor.status),
            parse_mode='html'
        )
        return RET.OK, None, None, None
