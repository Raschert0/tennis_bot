from flask_mongoengine import MongoEngine
from flask_admin.model import typefmt
from enum import IntEnum


db = MongoEngine()


class RDR(IntEnum):
    DO_NOTHING = 0
    NULLIFY = 1


class COMPETITOR_STATUS(IntEnum):
    UNATHORIZED = 0
    ACTIVE = 1
    CHALLENGE_INITIATED = 2  # When user sent challenge request to someone else
    CHALLENGE_NEED_RESPONSE = 3  # When user is answering to challenge request
    CHALLENGE = 4
    PASSIVE = 5
    VACATION = 6
    INJUIRY = 7
    INACTIVE = 8


class RESULT(IntEnum):
    A_WINS = 0
    B_WINS = 1
    DRAW = 2
    CANCELED = 3


class Config(db.Document):
    config_id = db.StringField()
    vacancy_time = db.IntField(default=14)
    time_to_accept_challenge = db.IntField(default=3)
    time_to_play_challenge = db.IntField(default=10)
    challenge_play_reminder = db.IntField(default=3)

    spreadsheet_id = db.StringField(default='1TE6stp-x7z-O7Rp3Twtg5oJ8Ytmlx7TTqRgDZ5bx39k')
    spreadsheet_users_sheet = db.StringField(default='Игроки')


class Competitor(db.Document):
    status = db.IntField(required=True)
    previous_status = db.IntField()
    name = db.StringField(required=True)
    level = db.IntField()
    matches = db.IntField(default=0)
    wins = db.IntField(default=0)
    losses = db.IntField(default=0)
    performance = db.IntField(default=0)

    remaining_vacancy_time = db.IntField(required=True)
    special_state_until = db.DateTimeField()

    dismissed_challenges = db.IntField(default=0)
    ignored_challenges = db.IntField(default=0)

    in_challenge_with = db.LazyReferenceField('self')

    legacy_number = db.StringField()

    meta = {'strict': False}


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


class Texts(db.Document):
    meta = {'strict': False}

    back_btn = db.StringField()
    skip_btn = db.StringField()


class Localization(db.Document):
    str_token = db.StringField(required=True)
    language = db.StringField(required=True)
    translation = db.StringField(required=True)
