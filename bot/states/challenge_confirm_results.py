from . import RET, BaseState
from localization.translations import get_translation_for

from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from models import User


class ChallengeConfirmResultsState(BaseState):
    pass
