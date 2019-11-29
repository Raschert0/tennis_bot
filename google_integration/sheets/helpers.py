from . import gsheets
from .usage_guard import guard
from googleapiclient.errors import HttpError
from logger_settings import logger


def retrieve_data(
        spreadsheetId,
        range,
        valueRenderOption='FORMATTED_VALUE',
        majorDimension='ROWS',
        dateTimeRenderOption='SERIAL_NUMBER'
):
    try:
        guard.account_forced_get()
        return gsheets.values().get(
            spreadsheetId=spreadsheetId,
            range=range,
            valueRenderOption=valueRenderOption,
            majorDimension=majorDimension,
            dateTimeRenderOption=dateTimeRenderOption
        ).execute()
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
        guard.account_forced_update()
        majorDimension = 'COLUMNS' if data_as_cols else 'ROWS'
        return gsheets.values().update(
            spreadsheetId=spreadsheetId,
            range=range,
            body={
                'values': values,
                'majorDimension': majorDimension
            },
            valueInputOption=valueInputOption
        ).execute()
    except HttpError as e:
        logger.exception('Exception occurred while updating spreadsheet')
        return None
