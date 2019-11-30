from flask_mongoengine import MongoEngine
from flask_admin.model import typefmt
from enum import IntEnum
from mongoengine.errors import DoesNotExist
from datetime import datetime


db = MongoEngine()


class RDR(IntEnum):
    DO_NOTHING = 0
    NULLIFY = 1


class COMPETITOR_STATUS:
    UNAUTHORIZED = 0
    ACTIVE = 1
    CHALLENGE_INITIATED = 2  # When user sent challenge request to someone else
    CHALLENGE_NEED_RESPONSE = 3  # When user is answering to challenge request
    CHALLENGE = 4
    CHALLENGE_NEED_RESULTS_CONFIRMATION = 5
    PASSIVE = 6
    VACATION = 7
    INJUIRY = 8
    INACTIVE = 9


class RESULT(IntEnum):
    A_WINS = 0
    B_WINS = 1
    DRAW = 2
    CANCELED = 3


class LOG_SEVERITY:
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    EXCEPTION = 'EXCEPTION'


class Config(db.Document):
    config_id = db.StringField()
    vacation_time = db.IntField(default=14)
    time_to_accept_challenge = db.IntField(default=3)
    time_to_play_challenge = db.IntField(default=10)
    challenge_play_reminder = db.IntField(default=3)
    maximum_level_difference = db.IntField(default=3)

    spreadsheet_id = db.StringField(default='1TE6stp-x7z-O7Rp3Twtg5oJ8Ytmlx7TTqRgDZ5bx39k')
    spreadsheet_users_sheet = db.StringField(default='Игроки')

    group_chat_id = db.IntField()

    last_daily_check = db.DateTimeField(default=datetime.utcnow())


class Competitor(db.Document):
    status = db.IntField(default=COMPETITOR_STATUS.UNAUTHORIZED)
    previous_status = db.IntField()
    name = db.StringField(required=True)
    level = db.IntField()
    matches = db.IntField(default=0)
    wins = db.IntField(default=0)
    losses = db.IntField(default=0)
    performance = db.IntField(default=0)

    used_vacation_time = db.IntField(default=0)
    vacation_started_at = db.DateTimeField()

    dismiss_confirmed = db.BooleanField()

    challenges_dismissed_in_a_row = db.IntField(default=0)
    challenges_ignored = db.IntField(default=0)

    challenges_dismissed_total = db.IntField(default=0)
    challenges_ignored_total = db.IntField(default=0)

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

    meta = {'strict': False}

    status_code_to_str_dict = {
        None: None,
        COMPETITOR_STATUS.UNAUTHORIZED: 'Unauthorized',
        COMPETITOR_STATUS.ACTIVE: 'Active',
        COMPETITOR_STATUS.CHALLENGE_INITIATED: 'Challenged',
        COMPETITOR_STATUS.CHALLENGE_NEED_RESPONSE: 'Challenged',
        COMPETITOR_STATUS.CHALLENGE: 'Challenged',
        COMPETITOR_STATUS.CHALLENGE_NEED_RESULTS_CONFIRMATION: 'Challenged',
        COMPETITOR_STATUS.PASSIVE: 'Passive',
        COMPETITOR_STATUS.VACATION: 'Vacation',
        COMPETITOR_STATUS.INJUIRY: 'Injuiry',
        COMPETITOR_STATUS.INACTIVE: 'Inactive'
    }


class User(db.Document):
    user_id = db.IntField(required=True)
    user_id_s = db.StringField()
    username = db.StringField()
    first_name = db.StringField()
    last_name = db.StringField()
    states = db.ListField(db.StringField())
    language = db.StringField(default='uk')

    is_blocked = db.BooleanField(default=False)

    associated_with = db.LazyReferenceField('Competitor', reverse_delete_rule=RDR.NULLIFY)

    def check_association(self):
        if not self.associated_with:
            return False
        try:
            return self.associated_with.fetch()
        except DoesNotExist:
            self.associated_with = None
            self.save()
            return False

    meta = {'strict': False}

    def __repr__(self):
        return f'User ({self.user_id} {self.username} {self.first_name} {self.last_name})'


class Result(db.Document):
    player_a = db.LazyReferenceField('Competitor', reverse_delete_rule=RDR.NULLIFY)
    player_b = db.LazyReferenceField('Competitor', reverse_delete_rule=RDR.NULLIFY)
    scores = db.ListField(db.StringField())
    result = db.IntField()

    meta = {'strict': False}


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
    severity = db.StringField
    log = db.StringField(required=True)

    @staticmethod
    def store_log(log: str, severity: str):
        log_document = HighLevelLogs(
            severity=severity,
            log=log
        )
        log_document.save()
