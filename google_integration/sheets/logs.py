from .helpers import retrieve_data, update_data
from bot.settings_interface import get_config
import logging
from logger_settings import hr_logger, logger
from datetime import datetime
from pytz import timezone


_k_tz = timezone('Europe/Kiev')
_logging_severity_to_str_dict = {
    logging.INFO: 'INFO',
    logging.ERROR: 'ERROR',
    logging.WARNING: 'WARNING'
}


class LogsSheet:

    @staticmethod
    def get_all_logs():
        cfg = get_config()
        if not cfg.spreadsheet_logs_sheet:
            return None
        values = retrieve_data(
            cfg.spreadsheet_id,
            f'{cfg.spreadsheet_logs_sheet}!A2:C'
        )
        if values is None:
            return None
        values = values.get('values', [])
        return values

    @staticmethod
    def glog(text: str, severity: logging.INFO, at_row=None):
        try:
            cfg = get_config()
            if not cfg.spreadsheet_logs_sheet:
                hr_logger.error('Не вдалося надіслати лог в гуглтаблицю - у налаштуваннях відсутня назва листа')
                logger.error('Cannot insert log into a google sheet - sheet name is missing')
                return

            if at_row is None:
                stored_logs = LogsSheet.get_all_logs()
                if stored_logs is None:
                    stored_logs = []
                at_row = len(stored_logs) + 2

            update_data(
                cfg.spreadsheet_id,
                f'{cfg.spreadsheet_logs_sheet}!A{at_row}:C',
                values=[
                    [
                        datetime.now(tz=_k_tz).strftime('%D/%m/%Y %H:%M:%S (%Z)'),
                        _logging_severity_to_str_dict[severity],
                        text
                    ]
                ]
            )
        except:
            logger.exception('Exception occurred while uploading log to gsheet')
