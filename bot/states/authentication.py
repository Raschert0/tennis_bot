from . import RET, BaseState
from localization.translations import get_translation_for

from telebot import TeleBot
from telebot.types import Message
from models import User

from google_integration.sheets.users import UsersSheet
from google_integration.sheets.usage_guard import guard
from models import Competitor, COMPETITOR_STATUS


class AuthenticationState(BaseState):

    def __init__(self):
        super().__init__()
        if guard.get_allowed()[0] and guard.update_allowed()[0]:
            UsersSheet.update_model()
            available_competitors = Competitor.objects(status=COMPETITOR_STATUS.UNATHORIZED)
            available_competitors_encoded_names = []
            for c in available_competitors:
                available_competitors_encoded_names.append(
                    f'{c.name}. {get_translation_for("level_str")}: ({c.level}).'
                )


