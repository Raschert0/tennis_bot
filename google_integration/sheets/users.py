from .helpers import retrieve_data, update_data
from models import Competitor, COMPETITOR_STATUS
from helpers import to_int
from bot.settings_interface import get_config_document
from logger_settings import logger


class UsersSheet:

    @staticmethod
    def get_all_users():
        cfg = get_config_document()
        values = retrieve_data(
            cfg.spreadsheet_id,
            f'{cfg.spreadsheet_users_sheet}!A2:H'
        )
        if values is None:
            return None
        values = values.get('values', [])
        return values

    @staticmethod
    def update_model():
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
                    cfg = get_config_document()
                    new_data = Competitor(
                        legacy_number=row[0],
                        name=row[1],
                        status=COMPETITOR_STATUS.UNAUTHORIZED,
                        level=to_int(row[3], None),
                        matches=to_int(row[4]),
                        wins=to_int(row[5]),
                        losses=to_int(row[6]),
                        performance=to_int(row[7]),
                        used_vacancy_time=0
                    )
                    new_data.save()
                    new_data.reload()
                    stored_in_sheet_records.add(new_data.id)
                else:
                    stored_in_sheet_records.add(existing_data.id)
                row_num += 1
            for new_record in Competitor.objects(id__not__in=stored_in_sheet_records):
                row_num += 1
                UsersSheet.insert_competitor_in_table(new_record, at_row=row_num)

    @staticmethod
    def insert_competitor_in_table(data: Competitor, check_for_existence=False, at_row=None):
        cfg = get_config_document()
        if check_for_existence:
            pass
        if at_row is None:
            already_inserted_data = UsersSheet.get_all_users()
            at_row = len(already_inserted_data) + 2
        update_data(
            cfg.spreadsheet_id,
            f'{cfg.spreadsheet_users_sheet}!A{at_row}:H',
            values=[
                [
                    data.legacy_number,
                    data.name,
                    Competitor.status_code_to_str_dict[data.status],
                    data.level or '',
                    data.matches,
                    data.wins,
                    data.losses,
                    data.performance
                ],
            ]
        )

    @staticmethod
    def update_competitor_status(competitor: Competitor, upsert=False):
        cfg = get_config_document()
        data = UsersSheet.get_all_users()
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
