from . import gsheets, __config as cfg
from .helpers import retrieve_data, update_data
from models import Competitor, COMPETITOR_STATUS
from helpers import to_int


class UsersSheet():

    status_code_to_str_dict = {
        COMPETITOR_STATUS.UNATHORIZED: 'Unauthorized',
        COMPETITOR_STATUS.ACTIVE: 'Active',
        COMPETITOR_STATUS.CHALLENGE_WAITING: 'Challenged',
        COMPETITOR_STATUS.CHALLENGE: 'Challenged',
        COMPETITOR_STATUS.PASSIVE: 'Passive',
        COMPETITOR_STATUS.VACATION: 'Vacation',
        COMPETITOR_STATUS.INJUIRY: 'Injuiry',
        COMPETITOR_STATUS.INACTIVE: 'Inactive'
    }

    @staticmethod
    def get_all_users():
        cfg.reload()
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
            for row_num, row in enumerate(data, 2):
                existing_data = Competitor.objects(
                    name=row[1],
                    legacy_number=row[0]
                ).first()
                if existing_data is None:
                    new_data = Competitor(
                        legacy_number=row[0],
                        name=row[1],
                        status=COMPETITOR_STATUS.UNATHORIZED,
                        level=to_int(row[3], None),
                        matches=to_int(row[4]),
                        wins=to_int(row[5]),
                        losses=to_int(row[6]),
                        performance=to_int(row[7]),
                        remaining_vacancy_time=cfg.vacancy_time
                    )
                    new_data.save()
                    new_data.reload()
                    stored_in_sheet_records.add(new_data.id)
                else:
                    stored_in_sheet_records.add(existing_data.id)
            for new_record in Competitor.objects(id__not__in=stored_in_sheet_records):
                row_num += 1
                UsersSheet.insert_competitor_in_table(new_record, at_row=row_num)


    @staticmethod
    def insert_competitor_in_table(data: Competitor, check_for_existence=False, at_row=None):
        cfg.reload()
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
                    UsersSheet.status_code_to_str_dict[data.status],
                    data.level or '',
                    data.matches,
                    data.wins,
                    data.losses,
                    data.performance
                ],
            ]
        )
