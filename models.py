from flask_mongoengine import MongoEngine
from flask_admin.model import typefmt
from enum import IntEnum
from mongoengine.errors import DoesNotExist
from datetime import datetime
from config import VERBOSE_HR_LOGS

db = MongoEngine()


class RDR(IntEnum):
    DO_NOTHING = 0
    NULLIFY = 1
    CASCADE = 2


class COMPETITOR_STATUS:
    UNAUTHORIZED = 0
    ACTIVE = 1
    PASSIVE = 2
    VACATION = 3
    INJUIRY = 4
    INACTIVE = 5
    CHALLENGE_INITIATED = 6  # When user sent challenge request to someone else
    CHALLENGE_NEED_RESPONSE = 7  # When user is answering to challenge request
    CHALLENGE_STARTER = 8  # When challenge is started and user is an initiator
    CHALLENGE_RECEIVER = 9  # When challenge is started
    CHALLENGE_NEED_RESULTS_CONFIRMATION = 10
    CHALLENGE_NEED_CANCELLATION_CONFIRMATION = 11


class RESULT(IntEnum):
    A_WINS = 0
    B_WINS = 1
    DRAW = 2
    CANCELED = 3
    DISMISSED = 4  # player_a wins
    IGNORED = 5  # player_a wins


class LOG_SEVERITY:
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    EXCEPTION = 'EXCEPTION'


class Config(db.Document):
    config_id = db.StringField()
    # vacation_time = db.IntField(default=14)
    # time_to_accept_challenge = db.IntField(default=3)
    # accept_challenge_reminder = db.IntField(default=2)
    # time_to_play_challenge = db.IntField(default=10)
    # challenge_play_reminder = db.IntField(default=3)
    # maximum_level_difference = db.IntField(default=3)
    # maximum_challenges_ignored = db.IntField(default=3)
    #
    # spreadsheet_id = db.StringField(default='1TE6stp-x7z-O7Rp3Twtg5oJ8Ytmlx7TTqRgDZ5bx39k')
    # spreadsheet_users_sheet = db.StringField(default='Игроки')
    #
    # group_chat_id = db.IntField()

    last_daily_check = db.DateTimeField(default=datetime.utcnow())


class Competitor(db.Document):
    status = db.IntField(default=COMPETITOR_STATUS.UNAUTHORIZED)
    previous_status = db.IntField()
    previous_challenge_status = db.IntField()
    name = db.StringField(required=True)
    level = db.IntField()
    matches = db.IntField(default=0)
    wins = db.IntField(default=0)
    losses = db.IntField(default=0)
    performance = db.IntField(default=0)

    used_vacation_time = db.IntField(default=0)
    vacation_started_at = db.DateTimeField()

    challenges_dismissed_in_a_row = db.IntField(default=0)
    challenges_ignored = db.IntField(default=0)

    challenges_dismissed_total = db.IntField(default=0)
    challenges_ignored_total = db.IntField(default=0)

    challenge_remainder_sent = db.BooleanField()

    in_challenge_with = db.LazyReferenceField('self')
    latest_challenge_sent_to = db.LazyReferenceField('self')

    latest_challenge_received_at = db.DateTimeField()
    challenge_started_at = db.DateTimeField()

    legacy_number = db.StringField()

    def check_opponent(self):
        if not self.in_challenge_with:
            return False
        try:
            return self.in_challenge_with.fetch()
        except DoesNotExist:
            try:
                op = Competitor.objects(in_challenge_with=self).first()
                if op is not None:
                    self.in_challenge_with = op
                    self.save()
                    return op
                else:
                    self.in_challenge_with = None
                    self.save()
                    return False
            except:
                self.in_challenge_with = None
                self.save()
                return False

    def change_status(self, new_status, bot=None):
        from google_integration.sheets.users import UsersSheet
        from localization.translations import get_translation_for
        from bot.settings_interface import get_config
        from telebot import TeleBot
        from config import BOT_TOKEN
        from logger_settings import hr_logger, logger

        update_sheet = False
        if self.status_code_to_str_dict[self.status] != self.status_code_to_str_dict[new_status]:
            update_sheet = True

        cfg = get_config()
        if update_sheet and cfg.admin_username:
            try:
                if self.status in (COMPETITOR_STATUS.INJUIRY, COMPETITOR_STATUS.INACTIVE) or \
                        new_status in (COMPETITOR_STATUS.INJUIRY, COMPETITOR_STATUS.INACTIVE):
                    admin_user = User.objects(username=cfg.admin_username).first()
                    if admin_user:
                        name = self.name
                        associated_user = self.get_relevant_user()
                        if associated_user:
                            name = f'<a href="tg://user?id={associated_user.user_id}">{name}</a>'
                        t = get_translation_for('admin_notification_competitor_changed_status').format(
                            name,
                            self.status,
                            new_status
                        )
                        if bot is None:
                            bot = TeleBot(BOT_TOKEN, threaded=False)
                        bot.send_message(
                            admin_user.user_id,
                            t,
                            parse_mode='html'
                        )
            except:
                logger.exception('Exception occurred while sending message to admin')
                hr_logger.error(f'Не вдалося надіслати адміністратору повідомлення про зміну стану користувача {self.name}')

        self.status = new_status
        if update_sheet:
            UsersSheet.update_competitor_status(self)

    def get_relevant_user(self):
        return User.objects(associated_with=self).first()

    meta = {'strict': False}

    status_code_to_str_dict = {
        None: None,
        COMPETITOR_STATUS.UNAUTHORIZED: 'Unauthorized',
        COMPETITOR_STATUS.ACTIVE: 'Active',
        COMPETITOR_STATUS.CHALLENGE_INITIATED: 'Challenged',
        COMPETITOR_STATUS.CHALLENGE_NEED_RESPONSE: 'Challenged',
        COMPETITOR_STATUS.CHALLENGE_STARTER: 'Challenged',
        COMPETITOR_STATUS.CHALLENGE_RECEIVER: 'Challenged',
        COMPETITOR_STATUS.CHALLENGE_NEED_RESULTS_CONFIRMATION: 'Challenged',
        COMPETITOR_STATUS.PASSIVE: 'Passive',
        COMPETITOR_STATUS.VACATION: 'Vacation',
        COMPETITOR_STATUS.INJUIRY: 'Injuiry',
        COMPETITOR_STATUS.INACTIVE: 'Inactive'
    }


class Result(db.Document):
    player_a = db.LazyReferenceField('Competitor', reverse_delete_rule=RDR.CASCADE)
    player_b = db.LazyReferenceField('Competitor', reverse_delete_rule=RDR.CASCADE)
    player_a_s = db.StringField()
    player_b_s = db.StringField()
    scores = db.ListField(db.IntField())
    scores_s = db.StringField()
    result = db.IntField()
    confirmed = db.BooleanField()
    canceled = db.BooleanField()
    date = db.DateTimeField()
    sent = db.BooleanField()
    level_change = db.StringField()

    meta = {'strict': False}

    result_to_str_dict = {
        None: None,
        RESULT.A_WINS: 'Виграш гравця A',
        RESULT.B_WINS: 'Виграш гравця B',
        RESULT.CANCELED: 'Canceled',
        RESULT.DRAW: 'Draw'
    }

    @staticmethod
    def try_to_parse_score(score):
        import re
        from helpers import to_int

        try:
            ret = []
            for ps in filter(None, re.split('[-,\s]', score)):
                i = to_int(ps, None)
                if i is None:
                    return None
                ret.append(i)
            return ret
        except:
            return None

    def repr_score(self):
        if not self.scores and self.scores_s:
            return self.scores_s
        score = None
        score_set = None
        for s in self.scores:
            if not score_set:
                score_set = f'{s}-'
            else:
                if score:
                    score += f', {score_set}{s}'
                else:
                    score = f'{score_set}{s}'
                score_set = None
        return score


class User(db.Document):
    user_id = db.IntField(required=True)
    user_id_s = db.StringField()
    username = db.StringField()
    first_name = db.StringField()
    last_name = db.StringField()
    states = db.ListField(db.StringField())
    language = db.StringField(default='uk')

    is_blocked = db.BooleanField(default=False)

    dismiss_confirmed = db.BooleanField()

    associated_with = db.LazyReferenceField('Competitor', reverse_delete_rule=RDR.NULLIFY)
    current_result = db.LazyReferenceField('Result', reverse_delete_rule=RDR.NULLIFY)

    def str_repr(self):
        if self.first_name:
            ret = self.first_name
            if self.last_name:
                ret += f' {self.last_name}'
            if self.username:
                ret += f'(@{self.username})'
            if VERBOSE_HR_LOGS:
                ret += f' tg://user?id={self.user_id}'
            return ret
        elif self.username:
            if VERBOSE_HR_LOGS:
                return f'@{self.username} tg://user?id={self.user_id}'
            else:
                return f'@{self.username}'
        else:
            if VERBOSE_HR_LOGS:
                return f'{self.user_id} tg://user?id={self.user_id}'
            else:
                return str(self.user_id)

    def check_association(self):
        if not self.associated_with:
            return False
        try:
            return self.associated_with.fetch()
        except DoesNotExist:
            self.associated_with = None
            self.save()
            return False

    def check_result(self):
        if not self.current_result:
            return False
        try:
            return self.current_result.fetch()
        except DoesNotExist:
            self.current_result = None
            self.save()
            return False

    meta = {'strict': False}

    def __repr__(self):
        return f'User ({self.user_id} {self.username} {self.first_name} {self.last_name})'


class Administrator(db.Document):
    username = db.StringField()
    password = db.StringField()

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __unicode__(self):
        return self.username


class Localization(db.Document):
    str_token = db.StringField(required=True)
    language = db.StringField(required=True)
    translation = db.StringField(required=True)


class HighLevelLogs(db.Document):
    date = db.DateTimeField(default=datetime.utcnow)
    severity = db.StringField(
        choices=(LOG_SEVERITY.INFO, LOG_SEVERITY.WARNING, LOG_SEVERITY.ERROR, LOG_SEVERITY.EXCEPTION))
    log = db.StringField(required=True)

    @staticmethod
    def store_log(log: str, severity: str):
        log_document = HighLevelLogs(
            severity=severity,
            log=log
        )
        log_document.save()
