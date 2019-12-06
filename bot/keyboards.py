from telebot import types
from localization.translations import get_translation_for
from models import COMPETITOR_STATUS
from logger_settings import logger


def get_keyboard_remover():
    keyboard = types.ReplyKeyboardRemove()
    return keyboard


def get_menu_keyboard(**kwargs):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    status = kwargs.get('status', COMPETITOR_STATUS.UNAUTHORIZED)
    if status == COMPETITOR_STATUS.UNAUTHORIZED:
        logger.error('Not provided status for keyboard in menu state. Asserting')
        assert False

    if status == COMPETITOR_STATUS.INACTIVE:
        return types.ReplyKeyboardRemove()

    if status in (COMPETITOR_STATUS.ACTIVE, COMPETITOR_STATUS.PASSIVE):
        keyboard.row(get_translation_for('menu_info_btn'),
                     get_translation_for('menu_create_challenge_btn'))
        keyboard.row(get_translation_for('menu_go_on_vacation_btn'),
                     get_translation_for('menu_go_on_sick_leave_btn'))
    elif status == COMPETITOR_STATUS.CHALLENGE_INITIATED:
        keyboard.row(get_translation_for('menu_info_btn'))
        keyboard.row(get_translation_for('menu_cancel_challenge_request_btn'))
    elif status == COMPETITOR_STATUS.CHALLENGE_NEED_RESPONSE:
        keyboard.row(get_translation_for('menu_info_btn'))
        keyboard.row(get_translation_for('menu_reply_to_challenge_request_btn'))
    elif status == COMPETITOR_STATUS.CHALLENGE_STARTER:
        keyboard.row(get_translation_for('menu_info_btn'))
        keyboard.row(get_translation_for('menu_submit_challenge_results_btn'))
        keyboard.row(get_translation_for('menu_cancel_challenge_btn'))
    elif status == COMPETITOR_STATUS.CHALLENGE_RECEIVER:
        keyboard.row(get_translation_for('menu_info_btn'))
        keyboard.row(get_translation_for('menu_submit_challenge_results_btn'))
    elif status == COMPETITOR_STATUS.CHALLENGE_NEED_CANCELLATION_CONFIRMATION:
        keyboard.row(get_translation_for('menu_info_btn'))
        keyboard.row(get_translation_for('challenge_cancel_request_opponent_confirm_btn'))
        keyboard.row(get_translation_for('challenge_cancel_request_opponent_dismiss_btn'))
    elif status == COMPETITOR_STATUS.CHALLENGE_NEED_RESULTS_CONFIRMATION:
        keyboard.row(get_translation_for('menu_info_btn'))
        keyboard.row(get_translation_for('menu_accept_challenge_results_btn'))
    elif status == COMPETITOR_STATUS.VACATION:
        keyboard.row(get_translation_for('menu_info_btn'))
        keyboard.row(get_translation_for('menu_end_vacation_btn'))
    elif status == COMPETITOR_STATUS.INJUIRY:
        keyboard.row(get_translation_for('menu_info_btn'))
        keyboard.row(get_translation_for('menu_end_sick_leave_btn'))
    return keyboard


def get_challenge_confirmation_keyboard(**kwargs):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        get_translation_for('challenge_received_accept_btn'),
        get_translation_for('challenge_received_dismiss_btn')
    )
    keyboard.row(get_translation_for('back_btn'))
    return keyboard


def get_results_keyboard(**kwargs):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    if kwargs.get('confirmation_stage', None):
        keyboard.row(
            get_translation_for('result_competitor_win_btn'),
            get_translation_for('result_opponent_win_btn')
        )
        keyboard.row(
            get_translation_for('results_confirm_btn')
        )
    else:
        for i in range(4):
            keyboard.row(
                str(4 * i),
                str(4 * i + 1),
                str(4 * i + 2),
                str(4 * i + 3),
            )
        keyboard.row(get_translation_for('results_scores_confirm_btn'))
    keyboard.row(
        get_translation_for('to_menu_btn'),
        get_translation_for('back_btn'),
        get_translation_for('results_clear_btn')
    )
    return keyboard


def get_result_confirmation_keyboard(**kwargs):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        get_translation_for('result_confirmation_confirm_btn'),
        get_translation_for('result_confirmation_dismiss_btn')
    )
    keyboard.row(get_translation_for('back_btn'))
    return keyboard
