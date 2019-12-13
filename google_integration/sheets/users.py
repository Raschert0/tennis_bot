from .helpers import retrieve_data, update_data
from models import Competitor, COMPETITOR_STATUS
from helpers import to_int
from bot.settings_interface import get_config
from logger_settings import logger, hr_logger


class UsersSheet:

    @staticmethod
    def get_all_users():
        cfg = get_config()
        values = retrieve_data(
            cfg.spreadsheet_id,
            f'{cfg.spreadsheet_users_sheet}!A2:H'
        )
        if values is None:
            return []
        values = values.get('values', [])
        return values

    @staticmethod
    def update_model(cleanse=True):
        data = UsersSheet.get_all_users()
        if not data:
            pass
        else:
            stored_in_sheet_records = set()
            row_num = 1
            for row in data:
                existing_data = Competitor.objects(
                    name=row[1],
                    legacy_number=row[0]
                ).first()
                if existing_data is None:
                    cfg = get_config()
                    new_data = Competitor(
                        legacy_number=row[0],
                        name=row[1],
                        status=COMPETITOR_STATUS.UNAUTHORIZED,
                        level=to_int(row[3], None),
                        matches=to_int(row[4]),
                        wins=to_int(row[5]),
                        losses=to_int(row[6]),
                        performance=to_int(row[7]),
                        used_vacation_time=0
                    )
                    new_data.save()
                    new_data.reload()
                    stored_in_sheet_records.add(new_data.id)
                else:
                    stored_in_sheet_records.add(existing_data.id)
                    UsersSheet.update_competitor_db_record(row, existing_data)
                row_num += 1
            for new_record in Competitor.objects(id__not__in=stored_in_sheet_records):
                if not cleanse:
                    row_num += 1
                    UsersSheet.insert_competitor_in_table(new_record, at_row=row_num)
                else:
                    new_record.delete()
            hr_logger.info('Оновлено список гравців з гугл-таблиці')

    @staticmethod
    def insert_competitor_in_table(data: Competitor, check_for_existence=False, at_row=None, all_data=None):
        cfg = get_config()
        if check_for_existence:
            pass
        data.reload()
        if not data.legacy_number:
            data.legacy_number = str(Competitor.objects.count() + 100)
            data.save()
        if at_row is None:
            if not all_data:
                already_inserted_data = UsersSheet.get_all_users()
            else:
                already_inserted_data = all_data
            at_row = len(already_inserted_data) + 2
        update_data(
            cfg.spreadsheet_id,
            f'{cfg.spreadsheet_users_sheet}!A{at_row}:G',
            values=[
                [
                    data.legacy_number,
                    data.name,
                    Competitor.status_code_to_str_dict[data.status],
                    data.level or '',
                    data.matches or 0,
                    data.wins or 0,
                    data.losses or 0
                ],
            ]
        )

    @staticmethod
    def update_competitor_status(competitor: Competitor, upsert=False, all_data=None):
        try:
            cfg = get_config()
            if not all_data:
                data = UsersSheet.get_all_users()
            else:
                data = all_data
            updated = False
            row_number = 1
            for row_number, row in enumerate(data, 2):
                if row[0] == competitor.legacy_number and row[1] == competitor.name:
                    update_data(
                        cfg.spreadsheet_id,
                        f'{cfg.spreadsheet_users_sheet}!C{row_number}',
                        values=[
                            [
                                Competitor.status_code_to_str_dict[competitor.status],
                            ]
                        ]
                    )
                    updated = True
                    break
            if not updated:
                if not upsert:
                    logger.error(f"Cannot update record for competitor {competitor.name} ({competitor.legacy_number}) - table record not found")
                else:
                    logger.warning(f"Cannot update record for competitor {competitor.name} ({competitor.legacy_number}) - table record not found. Performing upsert")
                    UsersSheet.insert_competitor_in_table(competitor, at_row=row_number+1)
        except:
            logger.exception('Exception occurred while updating competitor status in gsheet')

    @staticmethod
    def update_competitor_performance_from_table(competitor: Competitor, row=None):
        try:
            if row is None:
                data = UsersSheet.get_all_users()
                for row_number, row_data in enumerate(data, 2):
                    if row_data[0] == competitor.legacy_number and row_data[1] == competitor.name:
                        row = row_number
                        competitor.performance = to_int(row_data[7])
                        competitor.save()
                        break
                if row is None:
                    logger.error(f'Cannot get new performance for competitor: {competitor} - cannot found record in gsheet')
                return
            cfg = get_config()
            new_perf = retrieve_data(
                cfg.spreadsheet_id,
                f'{cfg.spreadsheet_users_sheet}!H{row}'
            )
            new_perf = to_int(new_perf, None)
            if new_perf is None:
                logger.error(f'Cannot get new performance for competitor: {competitor}')
                return
            competitor.performance = new_perf
            competitor.save()
        except:
            logger.exception(f'Error occurred while updating performance for competitor: {competitor}')

    @staticmethod
    def update_competitor_table_record(competitor: Competitor, all_data=None):
        try:
            cfg = get_config()
            if not all_data:
                data = UsersSheet.get_all_users()
            else:
                data = all_data
            updated = False
            row_number = 1
            for row_number, row in enumerate(data, 2):
                if row[0] == competitor.legacy_number and row[1] == competitor.name:
                    update_data(
                        cfg.spreadsheet_id,
                        f'{cfg.spreadsheet_users_sheet}!C{row_number}:G',
                        values=[
                            [
                                Competitor.status_code_to_str_dict[competitor.status],
                                competitor.level or '',
                                competitor.matches or 0,
                                competitor.wins or 0,
                                competitor.losses or 0
                            ]
                        ]
                    )
                    # UsersSheet.update_competitor_performance_from_table(
                    #     competitor,
                    #     row_number
                    # )
                    updated = True
                    break
            if not updated:
                logger.error(f"Cannot update record for competitor {competitor.name} ({competitor.legacy_number}) - table record not found")
        except:
            logger.exception('Exception occurred while updating competitor in gsheet')

    @staticmethod
    def update_competitor_db_record(table_row, competitor: Competitor):
        competitor.level = to_int(table_row[3], None)
        competitor.matches = to_int(table_row[4])
        competitor.wins = to_int(table_row[5])
        competitor.losses = to_int(table_row[6])
        competitor.performance = to_int(table_row[7])
        competitor.save()
