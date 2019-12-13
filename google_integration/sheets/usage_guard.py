from datetime import datetime
from logger_settings import logger


class UsageGuard:

    def __init__(self):
        self.__latest_selfcheck = datetime.now()
        self.__get_limits = 60
        self.__gets_per_100_seconds = 100
        self.__update_limits = 60
        self.__update_per_100_seconds = 100

    def __selfcheck(self):
        t = datetime.now()
        delta = t - self.__latest_selfcheck
        self.__latest_selfcheck = t
        s = delta.total_seconds()
        self.__get_limits = min(
            self.__gets_per_100_seconds / 100 * 60,
            self.__get_limits + self.__gets_per_100_seconds / 100 * s
        )
        self.__update_limits = min(
            self.__update_per_100_seconds / 100 * 60,
            self.__update_limits + self.__update_per_100_seconds / 100 * s
        )

    def get_allowed(self):
        self.__selfcheck()
        if self.__get_limits >= 1:
            return True, 0
        else:
            return False, -int(self.__get_limits)

    def update_allowed(self):
        self.__selfcheck()
        if self.__update_limits >= 1:
            return True, 0
        else:
            return False, -int(self.__update_limits)

    def account_forced_get(self):
        self.__selfcheck()
        self.__get_limits -= 1
        if self.__get_limits <= 10:
            logger.warning('Running out of get limit')

    def account_forced_update(self):
        self.__selfcheck()
        self.__update_limits -= 1
        if self.__update_limits <= 10:
            logger.warning('Running out of update limit')


guard = UsageGuard()
