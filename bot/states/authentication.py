from . import RET, BaseState
from localization.translations import get_translation_for

from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from models import User

from google_integration.sheets.users import UsersSheet
from google_integration.sheets.usage_guard import guard
from models import Competitor, COMPETITOR_STATUS
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from mongoengine.errors import ValidationError
from werkzeug.exceptions import NotFound
from logger_settings import logger
from bot.bot_methods import render_pagination
from helpers import to_int


class AuthenticationState(BaseState):

    def entry(self, message: Message, user: User, bot: TeleBot):
        if user.check_association():
            return RET.GO_TO_STATE, 'MenuState', message, user
        if guard.get_allowed()[0] and guard.update_allowed()[0]:
            UsersSheet.update_model()
        available_competitors = Competitor.objects(status=COMPETITOR_STATUS.UNAUTHORIZED).paginate(page=1, per_page=10)
        if not render_pagination(
            available_competitors,
            message,
            bot,
            get_translation_for('authentication_msg'),
            self.__base_keyboard
        ):
            bot.send_message(
                message.chat.id,
                get_translation_for('authentication_cannot_find_competitors_msg')
            )
        return RET.OK, None, None, None

    def process_callback(self, callback: CallbackQuery, user, bot: TeleBot):
        data = callback.data
        if data.find('auth_') != 0:
            return RET.ANSWER_CALLBACK, None, callback, user
        data = data.replace('auth_', '')
        if data.find('user=') == 0:
            ds = data.split('=')
            if len(ds) == 2:
                competitor_id = ds[1]
                try:
                    competitor = Competitor.objects(id=competitor_id).first()
                    if competitor is not None:
                        competitor.status = COMPETITOR_STATUS.ACTIVE
                        competitor.save()
                        user.associated_with = competitor
                        user.save()

                        competitor.reload()
                        UsersSheet.update_competitor_status(competitor)
                        return RET.ANSWER_AND_GO_TO_STATE, 'MenuState', callback, user
                    else:
                        return RET.ANSWER_CALLBACK, get_translation_for('authentication_specified_competitor_not_found_clb'), callback, user
                except ValidationError:
                    logger.exception(f'Incorrect competitor_id: {competitor_id} from user with user_id: {user.user_id}')
        elif data.find('paginate=') == 0:
            ds = data.split('=')
            if len(ds) == 2:
                page = ds[1]
                page = to_int(page, 1)
                try:
                    available_competitors = Competitor.objects(status=COMPETITOR_STATUS.UNAUTHORIZED).paginate(page=page,
                                                                                                              per_page=10)
                except NotFound:
                    logger.exception(f'User {user.user_id} tried to switch to nonexistent page {page}')
                    available_competitors = Competitor.objects(status=COMPETITOR_STATUS.UNAUTHORIZED).paginate(page=1,
                                                                                                              per_page=10)
                if not render_pagination(
                    available_competitors,
                    callback.message,
                    bot,
                    get_translation_for('authentication_msg'),
                    self.__base_keyboard,
                    update=True
                ):
                    bot.send_message(
                        callback.message.chat.id,
                        get_translation_for('authentication_cannot_find_competitors_msg')
                    )
        elif data.find('none') == 0:
            return RET.ANSWER_CALLBACK, None, callback, user
        elif data.find('refresh') == 0:
            if guard.get_allowed()[0] and guard.update_allowed()[0]:
                UsersSheet.update_model()
            available_competitors = Competitor.objects(status=COMPETITOR_STATUS.UNAUTHORIZED).paginate(page=1,
                                                                                                      per_page=10)
            if not render_pagination(
                    available_competitors,
                    callback.message,
                    bot,
                    get_translation_for('authentication_msg'),
                    self.__base_keyboard,
            ):
                bot.send_message(
                    callback.message.chat.id,
                    get_translation_for('authentication_cannot_find_competitors_msg')
                )
        return RET.ANSWER_CALLBACK, None, callback, user

    def __base_keyboard(self, **kwargs):
        keyboard = InlineKeyboardMarkup(row_width=1)
        for name, id_ in kwargs.get('names', []):
            keyboard.add(InlineKeyboardButton(
                name,
                callback_data=f'auth_user={id_}'
            ))
        if kwargs.get('has_pages', None) and kwargs.get('cur_page', None):
            end_row = [InlineKeyboardButton(
                '<',
                callback_data=f'auth_paginate={kwargs["cur_page"] - 1}' if kwargs.get('has_prev', None) else 'auth_none'
            ), InlineKeyboardButton(
                f'{kwargs["cur_page"]}{(" / " + str(kwargs["pages"]) if kwargs.get("pages", None) else "")}',
                callback_data='auth_none'
            ), InlineKeyboardButton(
                '>',
                callback_data=f'auth_paginate={kwargs["cur_page"] + 1}' if kwargs.get('has_next', None) else 'auth_none'
            ), InlineKeyboardButton(
                '🔄',
                callback_data='auth_refresh'
            )]
            keyboard.row(*end_row)
        return keyboard

