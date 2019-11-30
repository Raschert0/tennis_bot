from pytz import UTC


def is_digit(s):
    try:
        int(s)
        return True
    except:
        return False


def to_int(s, default=0):
    try:
        return int(s)
    except:
        return default


def user_last_state(user, default):
    if len(user.states):
        return user.states[len(user.states) - 1]
    return default


def mongo_time_to_local(mtime, tz):
    return mtime.replace(tzinfo=UTC).astimezone(tz)
