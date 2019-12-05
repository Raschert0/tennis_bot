from .helpers import retrieve_data, update_data
from bot.settings_interface import get_config
from logger_settings import hr_logger, logger
from pytz import timezone
from models import Result, Competitor, RESULT
from helpers import mongo_time_to_local
from datetime import datetime
from localization.translations import get_translation_for
from telebot import TeleBot
from config import BOT_TOKEN

_k_tz = timezone('Europe/Kiev')


class ResultsSheet:

    @staticmethod
    def get_all_successful_results():
        cfg = get_config()
        if not cfg.spreadsheet_results_sheet:
            return None
        values = retrieve_data(
            cfg.spreadsheet_id,
            f'{cfg.spreadsheet_results_sheet}!A2:E'
        )
        if values is None:
            return None
        values = values.get('values', [])
        if values:
            try:
                for v in values:
                    while len(v) < 5:
                        v.append('')
            except:
                logger.exception('Error!')
        return values

    @staticmethod
    def get_all_canceled_results():
        cfg = get_config()
        if not cfg.spreadsheet_results_sheet:
            return None
        values = retrieve_data(
            cfg.spreadsheet_id,
            f'{cfg.spreadsheet_results_sheet}!H2:L'
        )
        if values is None:
            return None
        values = values.get('values', [])
        return values

    @staticmethod
    def upload_result(result: Result, at_row=None):
        try:
            cfg = get_config()
            if not cfg.spreadsheet_results_sheet:
                hr_logger.error(
                    'Не вдалося надіслати результат матчу в гуглтаблицю - у налаштуваннях відсутня назва листа')
                logger.error('Cannot insert result into a google sheet - sheet name is missing')
                return

            if at_row is None:
                results = ResultsSheet.get_all_successful_results()
                if results is None:
                    results = []
                at_row = len(results) + 2

            if result.result in (RESULT.A_WINS, RESULT.B_WINS):
                winner = result.player_a.fetch() if result.result == RESULT.A_WINS else result.player_b.fetch()
                looser = result.player_b.fetch() if result.result == RESULT.A_WINS else result.player_a.fetch()
                score = result.repr_score()

                update_data(
                    cfg.spreadsheet_id,
                    f'{cfg.spreadsheet_results_sheet}!A{at_row}:E',
                    values=[
                        [
                            mongo_time_to_local(result.date, tz=_k_tz).strftime('%d/%m/%Y'),
                            winner.name,
                            score,
                            looser.name,
                            result.level_change or '-'
                        ]
                    ]
                )
            else:
                logger.error(f"Wrong method called for result {result.id}. Call upload_canceled_result instead")
        except:
            logger.exception('Exception occurred while uploading match result')

    @staticmethod
    def upload_canceled_result(winner: Competitor, looser: Competitor, level_change=None, was_dismissed=False,
                               was_ignored=False, at_row=None):
        try:
            if not was_dismissed and not was_ignored:
                logger.error(
                    'upload_canceled_result called without both was_dismissed and was_ignored - one must be set')
                return
            if was_dismissed and was_ignored:
                logger.error(
                    'upload_canceled_result called with both was_dismissed and was_ignored - only one must be set')
                return

            cfg = get_config()
            if not cfg.spreadsheet_results_sheet:
                hr_logger.error(
                    'Не вдалося надіслати результат матчу в гуглтаблицю - у налаштуваннях відсутня назва листа')
                logger.error('Cannot insert result into a google sheet - sheet name is missing')
                return

            if not at_row:
                results = ResultsSheet.get_all_canceled_results()
                if results is None:
                    results = []
                at_row = len(results) + 2

            t = ''
            if was_ignored:
                t = get_translation_for('gsheet_technical_win_ignored_str')
            if was_dismissed:
                t = get_translation_for('gsheet_technical_win_dismissed_str')

            update_data(
                cfg.spreadsheet_id,
                f'{cfg.spreadsheet_results_sheet}!H{at_row}:L',
                values=[
                    [
                        datetime.now(tz=_k_tz).strftime('%d/%m/%Y'),
                        looser.name,
                        t,
                        winner.name,
                        level_change or '-'
                    ]
                ]
            )
        except:
            logger.exception('Exception occurred while uploading canceled match results')

    @staticmethod
    def synchronize_results(max_delta=None):
        all_finished_matches = ResultsSheet.get_all_successful_results()
        all_canceled_matches = ResultsSheet.get_all_canceled_results()

        stored_results = []
        for result in Result.objects(confirmed=True):
            stored_results.append(result)

        for sr in stored_results:
            sr: Result
            score = sr.repr_score()
            date = mongo_time_to_local(sr.date, _k_tz).strftime('%d/%m/%Y')

            found = False
            for fm in all_finished_matches:
                if fm[0] == date and \
                        fm[1] == sr.player_a_s and \
                        fm[2] == score and \
                        fm[3] == sr.player_b_s:
                    found = True
                    all_finished_matches.remove(fm)
                    break
            if not found:
                if sr.deletion_marker:
                    logger.error(f'Again cannot find result info in gsheet: {sr.id}. Deleting')
                    sr.delete()
                else:
                    logger.error(f'Cannot find result info in gsheet: {sr.id}')
                    sr.deletion_marker = True
                    sr.save()

            else:
                sr.deletion_marker = False
                sr.save()

        now = datetime.now(tz=_k_tz)
        tbot = None
        for new_record in all_finished_matches:
            try:
                nr_date = new_record[0]
                try:
                    nr_date = datetime.strptime(nr_date, '%d/%m/%Y')
                except ValueError:
                    nr_date = datetime.strptime(nr_date, '%m/%d/%Y')
                nr_date = _k_tz.localize(nr_date)
                score = Result.try_to_parse_score(new_record[2])
                score_s = None
                if score is None:
                    score_s = new_record[2]
                    score = []
                new_res = Result(
                    player_a_s = new_record[1],
                    player_b_s = new_record[3],
                    scores=score,
                    scores_s=score_s,
                    confirmed=True,
                    level_change=new_record[4],
                    date=nr_date,
                    result=RESULT.A_WINS
                )
                new_res.save()

                cfg = get_config()
                if cfg.group_chat_id and (nr_date > now or (max_delta and (now - nr_date) < max_delta)):
                    if tbot is None:
                        tbot = TeleBot(BOT_TOKEN, threaded=False)

                    score = new_res.repr_score()
                    gmsg = get_translation_for('group_chat_match_result_msg').format(new_res.player_a_s,
                                                                                     new_res.player_b_s,
                                                                                     score)
                    if new_res.level_change:
                        gmsg += '.\n'
                        gmsg += get_translation_for('group_chat_players_level_changed').format(new_res.level_change)

                    try:
                        tbot.send_message(
                            cfg.group_chat_id,
                            gmsg,
                            parse_mode='html'
                        )
                    except:
                        logger.exception('Exception occurred while sending message to group chat')
            except:
                logger.exception(f'Exception occurred while checking new_record: {new_record}')

        # CANCELED CHECKS

        stored_results = []
        for result in Result.objects(canceled=True):
            stored_results.append(result)

        for sr in stored_results:
            sr: Result
            date = mongo_time_to_local(sr.date, _k_tz).strftime('%d/%m/%Y')

            found = False
            for fm in all_canceled_matches:
                is_ignored = fm[2].find('игнор') != -1 or fm[2].find('проігнор') != -1
                is_dismissed = fm[2].find('повторн') != -1 or fm[2].find('відмов') != -1
                if fm[0] == date and \
                        fm[3] == sr.player_a_s and \
                        fm[1] == sr.player_b_s and \
                        ((is_dismissed and sr.result == RESULT.DISMISSED) or (is_ignored and sr.result == RESULT.IGNORED)):
                    found = True
                    all_canceled_matches.remove(fm)
                    break
            if not found:
                if sr.deletion_marker:
                    logger.error(f'Again cannot find result info in gsheet: {sr.id}')
                    sr.delete()
                else:
                    logger.error(f'Cannot find result info in gsheet: {sr.id}')
                    sr.deletion_marker = True
                    sr.save()
            else:
                sr.deletion_marker = False
                sr.save()

        for new_record in all_canceled_matches:
            try:
                nr_date = new_record[0]
                try:
                    nr_date = datetime.strptime(nr_date, '%d/%m/%Y')
                except ValueError:
                    nr_date = datetime.strptime(nr_date, '%m/%d/%Y')
                nr_date = _k_tz.localize(nr_date)
                is_ignored = new_record[2].find('игнор') != -1 or new_record[2].find('проігнор') != -1
                #is_dismissed = new_record[2].find('повторн') != -1 or new_record[2].find('відмов') != -1
                new_res = Result(
                    player_a_s = new_record[3],
                    player_b_s = new_record[1],
                    canceled=True,
                    level_change=new_record[4],
                    date=nr_date,
                    result=RESULT.IGNORED if is_ignored else RESULT.DISMISSED
                )
                new_res.save()

                cfg = get_config()
                if cfg.group_chat_id and (nr_date > now or (max_delta and (now - nr_date) < max_delta)):
                    if tbot is None:
                        tbot = TeleBot(BOT_TOKEN, threaded=False)

                    if is_ignored:
                        gmsg = get_translation_for('gsheet_log_player_ignored_challenge_from_player').format(
                            new_res.player_b_s,
                            new_res.player_a_s
                        )
                    else:
                        gmsg = get_translation_for('gsheet_log_player_dismissed_challenge_from_player').format(
                            new_res.player_b_s,
                            new_res.player_a_s
                        )

                    if new_res.level_change:
                        gmsg += '.\n'
                        gmsg += get_translation_for('group_chat_players_level_changed').format(new_res.level_change)

                    try:
                        tbot.send_message(
                            cfg.group_chat_id,
                            gmsg,
                            parse_mode='html'
                        )
                    except:
                        logger.exception('Exception occurred while sending message to group chat')
            except:
                logger.exception(f'Exception occurred while checking new_record: {new_record}')
