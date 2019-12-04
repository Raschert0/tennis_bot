from .helpers import retrieve_data, update_data
from bot.settings_interface import get_config
from logger_settings import hr_logger, logger
from pytz import timezone
from models import Result, Competitor, RESULT
from helpers import mongo_time_to_local
from datetime import datetime
from localization.translations import get_translation_for


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
        return values

    @staticmethod
    def get_all_canceled_results():
        cfg = get_config()
        if not cfg.spreadsheet_results_sheet:
            return None
        values = retrieve_data(
            cfg.spreadsheet_id,
            f'{cfg.spreadsheet_results_sheet}!H2:K'
        )
        if values is None:
            return None
        values = values.get('values', [])
        return values

    @staticmethod
    def upload_result(result: Result, at_row = None):
        try:
            cfg = get_config()
            if not cfg.spreadsheet_results_sheet:
                hr_logger.error('Не вдалося надіслати результат матчу в гуглтаблицю - у налаштуваннях відсутня назва листа')
                logger.error('Cannot insert result into a google sheet - sheet name is missing')
                return

            if at_row is None:
                results = ResultsSheet.get_all_successful_results()
                if results is None:
                    results = []
                at_row = len(results) + 2

            winner = result.player_a.fetch() if result.result == RESULT.A_WINS else result.player_b.fetch()
            looser = result.player_b.fetch() if result.result == RESULT.A_WINS else result.player_a.fetch()
            score = None
            score_set = None
            for s in result.scores:
                if not score_set:
                    score_set = f'{s}-'
                else:
                    if score:
                        score += f', {score_set}{s}'
                    else:
                        score = f'{score_set}{s}'
                    score_set = None

            update_data(
                cfg.spreadsheet_id,
                f'{cfg.spreadsheet_results_sheet}!A{at_row}:E',
                values=[
                    [
                        mongo_time_to_local(result.date, tz=_k_tz).strftime('%D/%m/%Y'),
                        winner.name,
                        score,
                        looser.name,
                        result.level_change or '-'
                    ]
                ]
            )
        except:
            logger.exception('Exception occurred while uploading match result')

    @staticmethod
    def upload_canceled_result(winner: Competitor, looser: Competitor, level_change=None, was_dismissed=False, was_ignored=False, at_row=None):
        try:
            if not was_dismissed and not was_ignored:
                logger.error('upload_canceled_result called without both was_dismissed and was_ignored - one must be set')
                return
            if was_dismissed and was_ignored:
                logger.error('upload_canceled_result called with both was_dismissed and was_ignored - only one must be set')
                return

            cfg = get_config()
            if not cfg.spreadsheet_results_sheet:
                hr_logger.error('Не вдалося надіслати результат матчу в гуглтаблицю - у налаштуваннях відсутня назва листа')
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
                        datetime.now(tz=_k_tz).strftime('%D/%m/%Y'),
                        looser.name,
                        t,
                        winner.name,
                        level_change or '-'
                    ]
                ]
            )
        except:
            logger.exception('Exception occurred while uploading canceled match results')
