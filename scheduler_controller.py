from time import sleep
import schedule
import multiprocessing
import logging
import atexit
from datetime import datetime, timedelta
from pytz import timezone
from logger_settings import logger
from bot.settings_interface import get_config_document



def __scheduler_run(cease_run, interval=60):

    def daily_task():
        from models import Competitor, COMPETITOR_STATUS, User
        from config import BOT_TOKEN
        from telebot import TeleBot
        from localization.translations import get_translation_for
        from bot.keyboards import get_menu_keyboard
        from google_integration.sheets.users import UsersSheet

        tz = timezone('Europe/Kiev')
        now = datetime.now(tz=tz)
        tbot = None
        config = get_config_document()
        for competitor in Competitor.objects(status=COMPETITOR_STATUS.VACATION):
            if competitor.vacation_started_at:
                delta = now - competitor.vacation_started_at.astimezone(tz)
                delta = delta.total_seconds()
                if competitor.used_vacation_time is not None:
                    delta += competitor.used_vacation_time
                if timedelta(seconds=delta).days > config.vacation_time:
                    competitor.status = competitor.previous_status or COMPETITOR_STATUS.ACTIVE
                    competitor.save()
                    relevant_user: User = User.objects(associated_with=competitor).first()
                    if relevant_user is not None:
                        if not tbot:
                            tbot = TeleBot(BOT_TOKEN)
                        tbot.send_message(
                            relevant_user.user_id,
                            get_translation_for('menu_on_vacation_end_msg'),
                            reply_markup=get_menu_keyboard(status=competitor.status)
                        )
                    UsersSheet.update_competitor_status(competitor)
            else:
                logger.error(f"Cannot find vacation_started_at for competitor {competitor.name} (on vacation). Saved current time")
                competitor.vacation_started_at = now
                competitor.save()


    def daily_task_check():
        config = get_config_document()
        n = datetime.now(tz=timezone('Europe/Kiev'))
        if config.last_daily_check:
            lc = config.last_daily_check.astimezone(timezone('Europe/Kiev'))
            if (n - lc) > timedelta(hours=3) and n.hour in (8, 9, 10):
                logger.info(f'Performing daily task at {n}')
                config.last_daily_check = n
                config.save()
                daily_task()

    schedule.logger.setLevel(logging.WARNING)
    schedule.every(5).minutes.do(daily_task_check)
    logging.info('Test')
    logging.error('Test2')

    while not cease_run.is_set():
        schedule.run_pending()
        sleep(interval)


def schedule_controller():
    cease_continuous_run = multiprocessing.Event()

    p = multiprocessing.Process(target=__scheduler_run, args=(cease_continuous_run, 1))
    p.start()

    atexit.register(p.terminate)
    atexit.register(cease_continuous_run.set)

    return cease_continuous_run


if __name__ == '__main__':
    schedule_controller()
