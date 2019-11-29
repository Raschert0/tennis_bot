from telebot import types
from localization.translations import get_translation_for


def get_base_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Test keyboard')
    return keyboard


def get_main_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(get_translation_for(''))
    return keyboard


def get_keyboard_remover():
    keyboard = types.ReplyKeyboardRemove()
    return keyboard
