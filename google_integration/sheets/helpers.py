from . import gsheets
from .usage_guard import guard
from googleapiclient.errors import HttpError
from logger_settings import logger
from datetime import datetime


def retrieve_data(
        spreadsheetId,
        range,
        valueRenderOption='FORMATTED_VALUE',
        majorDimension='ROWS',
        dateTimeRenderOption='SERIAL_NUMBER'
):
    try:
        logger.debug(f'Started retrieving data at {datetime.now()}')
        guard.account_forced_get()
        data = gsheets.values().get(
            spreadsheetId=spreadsheetId,
            range=range,
            valueRenderOption=valueRenderOption,
            majorDimension=majorDimension,
            dateTimeRenderOption=dateTimeRenderOption
        ).execute()
        logger.debug(f'Finished retrieving data at {datetime.now()}')
        return data
    except HttpError as e:
        logger.exception('Exception occurred while retrieving data from spreadsheet')
        return None


def update_data(
        spreadsheetId,
        range,
        values,
        data_as_cols=False,
        valueInputOption='USER_ENTERED'
):
    try:
        logger.debug(f'Started data update at {datetime.now()}')
        guard.account_forced_update()
        majorDimension = 'COLUMNS' if data_as_cols else 'ROWS'
        result = gsheets.values().update(
            spreadsheetId=spreadsheetId,
            range=range,
            body={
                'values': values,
                'majorDimension': majorDimension
            },
            valueInputOption=valueInputOption
        ).execute()
        logger.debug(f'Finished data update at {datetime.now()}')
        return result
    except HttpError as e:
        logger.exception('Exception occurred while updating spreadsheet')
        return None
