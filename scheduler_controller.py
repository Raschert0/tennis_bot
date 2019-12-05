from time import sleep
import schedule
import multiprocessing
import logging
import atexit
from datetime import datetime, timedelta
from pytz import timezone
from logger_settings import logger
from bot.settings_interface import get_config_document, get_config
from helpers import mongo_time_to_local
from models import db
from config import PROJECT_NAME


def __scheduler_run(cease_run, interval=60):
    from models import Competitor, COMPETITOR_STATUS, User
    from config import BOT_TOKEN
    from telebot import TeleBot
    from localization.translations import get_translation_for
    from bot.keyboards import get_menu_keyboard
    from bot.bot_methods import get_opponent_and_opponent_user
    from google_integration.sheets.users import UsersSheet
    from google_integration.sheets.matches import ResultsSheet
    from google_integration.sheets.logs import LogsSheet
    from config import DB_PASSWORD, DB_USER

    print('*Scheduler started*')
    db.disconnect()
    db.connect(PROJECT_NAME, username=DB_USER, password=DB_PASSWORD)
    tz = timezone('Europe/Kiev')

    def daily_task():
        tz = timezone('Europe/Kiev')
        now = datetime.now(tz=tz)
        tbot = None
        bconfig = get_config()
        for competitor in Competitor.objects(status=COMPETITOR_STATUS.VACATION):
            if competitor.vacation_started_at:
                delta = now - mongo_time_to_local(competitor.vacation_started_at, tz)
                delta = delta.total_seconds()
                if competitor.used_vacation_time is not None:
                    delta += competitor.used_vacation_time
                if timedelta(seconds=delta).days > bconfig.vacation_time:
                    competitor.change_status(competitor.previous_status or COMPETITOR_STATUS.ACTIVE)
                    competitor.save()
                    relevant_user: User = User.objects(associated_with=competitor).first()
                    if relevant_user is not None:
                        if not tbot:
                            tbot = TeleBot(BOT_TOKEN, threaded=False)
                        tbot.send_message(
                            relevant_user.user_id,
                            get_translation_for('menu_on_vacation_end_msg'),
                            reply_markup=get_menu_keyboard(status=competitor.status)
                        )
            else:
                logger.error(f"Cannot find vacation_started_at for competitor {competitor.name} (on vacation). Saved current time")
                competitor.vacation_started_at = now
                competitor.save()

    def daily_task_check():
        config = get_config_document()
        n = datetime.now(tz=tz)
        if config.last_daily_check:
            lc = mongo_time_to_local(config.last_daily_check, tz)
            if (n - lc) > timedelta(hours=3) and n.hour in (8, 9, 10):
                logger.info(f'Performing daily task at {n}')
                config.last_daily_check = n
                config.save()
                daily_task()
        else:
            config.last_daily_check = n
            config.save()

    def check_challenges():
        bconfig = get_config()
        n = datetime.now(tz=tz)
        tbot = None
        for competitor in Competitor.objects(status=COMPETITOR_STATUS.CHALLENGE_NEED_RESPONSE):
            try:
                if not competitor.latest_challenge_received_at:
                    logger.error(f'Competitor {competitor.name} {competitor.legacy_number} has no latest_challenge_received_at')
                    competitor.latest_challenge_received_at = datetime.now(tz=tz)
                    competitor.save()
                    continue
                cs = mongo_time_to_local(competitor.challenge_started_at, tz)
                if (cs - n) > timedelta(days=max(0, bconfig.time_to_accept_challenge-bconfig.accept_challenge_reminder)) and not competitor.challenge_remainder_sent:
                    if tbot is None:
                        tbot = TeleBot(PROJECT_NAME, threaded=False)
                    cuser = User.objects(associated_with=competitor).first()
                    if cuser is None:
                        continue
                    tbot.send_message(
                        cuser.user_id,
                        get_translation_for('remainder_challenge_accept_msg').format(bconfig.accept_challenge_reminder)
                    )
                    competitor.challenge_remainder_sent = True
                    competitor.save()
                elif (cs-n) > timedelta(days=bconfig.time_to_accept_challenge):
                    if tbot is None:
                        tbot = TeleBot(PROJECT_NAME, threaded=False)
                    cuser = User.objects(associated_with=competitor).first()
                    skip_comp = False
                    if cuser is None:
                        skip_comp = True

                    opponent_user: User
                    opponent, opponent_user = get_opponent_and_opponent_user(competitor)

                    prev_level, new_level = None, None
                    level_change = None
                    if opponent and opponent.level > competitor.level:
                        new_level = competitor.level
                        prev_level = opponent.level
                        level_change = f'{prev_level}->{new_level}'
                        ResultsSheet.upload_canceled_result(opponent, competitor, level_change, was_ignored=True)

                    if opponent:
                        config = get_config()
                        if config.group_chat_id:
                            gmsg = get_translation_for('group_chat_technical_win_report_msg').format(opponent.name,
                                                                                                     competitor.name)
                            if level_change:
                                gmsg += '.\n'
                                gmsg += get_translation_for('group_chat_players_level_changed').format(level_change)

                                LogsSheet.glog(
                                    get_translation_for('gsheet_log_player_ignored_challenge_from_player').format(
                                        competitor.name,
                                        opponent.name
                                    ) + '. ' + get_translation_for('group_chat_players_level_changed').format(level_change)
                                )
                            else:
                                LogsSheet.glog(
                                    get_translation_for('gsheet_log_player_ignored_challenge_from_player').format(
                                        competitor.name,
                                        opponent.name
                                    )
                                )

                            try:
                                tbot.send_message(
                                    config.group_chat_id,
                                    gmsg,
                                    parse_mode='html'
                                )
                            except:
                                logger.exception('Exception occurred while sending message to group chat')

                    competitor.in_challenge_with = None
                    competitor.change_status(competitor.previous_status)
                    competitor.previous_status = None
                    competitor.latest_challenge_received_at = None
                    if prev_level:
                        competitor.level = prev_level

                    competitor.challenges_ignored = (competitor.challenges_ignored + 1) if competitor.challenges_ignored is not None else 1
                    competitor.challenges_ignored_total = (
                                competitor.challenges_ignored_total + 1) if competitor.challenges_ignored_total is not None else 1
                    competitor.matches = competitor.matches + 1 if competitor.matches is not None else 1
                    if competitor.challenges_ignored >= bconfig.maximum_challenges_ignored:
                        competitor.change_status(COMPETITOR_STATUS.INACTIVE)
                        LogsSheet.glog(
                            get_translation_for('gsheet_log_player_moved_to_inactive').format(competitor.name)
                        )
                    competitor.save()
                    UsersSheet.update_competitor_table_record(competitor)

                    t = get_translation_for('challenge_was_ignored_msg').format(
                            competitor.challenges_ignored,
                            bconfig.maximum_challenges_ignored
                        )

                    if not skip_comp:
                        if competitor.status == COMPETITOR_STATUS.INACTIVE:
                            t += '.\n<b>'
                            t += get_translation_for('user_was_moved_to_inactive')
                            t += '</b>'
                        elif prev_level:
                            t += '.\n'
                            t += get_translation_for('your_level_changed_str').format(new_level, prev_level)

                        tbot.send_message(
                            cuser.user_id,
                            t,
                            reply_markup=get_menu_keyboard(
                                status=competitor.status
                            ),
                            parse_mode='html'
                        )

                    if opponent:
                        opponent.in_challenge_with = None
                        opponent.change_status(opponent.previous_status)
                        opponent.previous_status = None
                        opponent.latest_challenge_received_at = None
                        opponent.wins = opponent.wins + 1 if opponent.wins is not None else 1
                        opponent.matches = opponent.matches + 1 if opponent.matches is not None else 1
                        opponent.save()
                        UsersSheet.update_competitor_table_record(opponent)

                        t = get_translation_for('challenge_was_ignored_opponent_msg')
                        if prev_level:
                            t += '\n'
                            t += get_translation_for('your_level_changed_str').format(prev_level, new_level)
                        if opponent_user:
                            tbot.send_message(
                                opponent_user.user_id,
                                t,
                                reply_markup=get_menu_keyboard(status=opponent.status),
                                parse_mode='html'
                            )
            except:
                logger.exception(f'Exception occurred while checking challenge requests for competitor {competitor.name} {competitor.legacy_number}')

        for competitor in Competitor.objects(
                status__in=(
                    COMPETITOR_STATUS.CHALLENGE_STARTER,
                    COMPETITOR_STATUS.CHALLENGE_RECEIVER,
                    COMPETITOR_STATUS.CHALLENGE_NEED_RESULTS_CONFIRMATION,
                    COMPETITOR_STATUS.CHALLENGE_NEED_CANCELLATION_CONFIRMATION
                )
        ):
            try:
                if not competitor.challenge_started_at:
                    logger.error(f'Competitor {competitor.name} {competitor.legacy_number} has no challenge_started_at')
                    competitor.challenge_started_at = datetime.now(tz=tz)
                    competitor.save()
                    continue
                cs = mongo_time_to_local(competitor.challenge_started_at, tz)
                if (cs - n) > timedelta(days=max(0, bconfig.time_to_play_challenge-bconfig.challenge_play_reminder)):
                    if tbot is None:
                        tbot = TeleBot(PROJECT_NAME, threaded=False)
                    cuser = User.objects(associated_with=competitor).first()
                    if cuser is None:
                        continue
                    tbot.send_message(
                        cuser.user_id,
                        get_translation_for('remainder_challenge_play_msg').format(bconfig.challenge_play_reminder)
                    )
                    competitor.challenge_remainder_sent = True
                    competitor.save()
                elif (cs - n) > timedelta(days=bconfig.time_to_play_challenge):
                    # TODO
                    pass
            except:
                logger.exception(f'Exception occurred while checking challenges in progress (for competitor {competitor.name} {competitor.legacy_number})')

    schedule.logger.setLevel(logging.WARNING)
    schedule.every(5).minutes.do(daily_task_check)
    schedule.every(30).seconds.do(check_challenges)

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
