from googleapiclient.discovery import build
from google.oauth2 import service_account

import os

from google2pandas.helpers import ValidateSetterProperty, scope_validation


class SheetRelay:

    sheet_scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    drive_scopes = ["https://www.googleapis.com/auth/drive.readonly"]

    def __init__(self, key_file=None, page_size=100, **kwargs):
        self.key_file = key_file
        self._sheet_credentials = service_account.Credentials.from_service_account_file(
            self.key_file
        ).with_scopes(self.sheet_scopes)
        self._drive_credentials = service_account.Credentials.from_service_account_file(
            self.key_file
        ).with_scopes(self.drive_scopes)
        self._sheet_service = build(
            "sheets",
            "v4",
            credentials=self._sheet_credentials,
            http=kwargs.get("http", None),
            developerKey=kwargs.get("developerKey", None),
            model=kwargs.get("model", None),
            cache_discovery=kwargs.get("cache_discovery", True),
            cache=kwargs.get("cache", None),
        )
        self._drive_service = build(
            "drive",
            "v3",
            credentials=self._drive_credentials,
            http=kwargs.get("http", None),
            developerKey=kwargs.get("developerKey", None),
            model=kwargs.get("model", None),
            cache_discovery=kwargs.get("cache_discovery", True),
            cache=kwargs.get("cache", None),
        )
        self._file_list = self._get_file_list(page_size)

    # Instace Variable Functions
    @ValidateSetterProperty
    def key_file(self, input_key_file):
        if input_key_file == None:
            key_file_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        else:
            key_file_path = input_key_file

        if not os.path.isfile(key_file_path):
            raise OSError(
                "Either the enviroment variable GOOGLE_APPLICATION_CRDENTIALS is incorrect or does not exist,\n"
                "or the key file path inputted does not exist"
            )

        return key_file_path

    def _get_file_list(self, page_size):
        response = (
            self._drive_service.files()
            .list(
                pageSize=page_size,
                q="mimeType='application/vnd.google-apps.spreadsheet'",
            )
            .execute()
        )

        file_list = response["files"]

        while response["incompleteSearch"]:
            response = (
                self._drive_service.files()
                .list(
                    pageSize=page_size,
                    q="mimeType='application/vnd.google-apps.spreadsheet'",
                    pageToken=response["nextPageToken"],
                )
                .execute()
            )

            file_list + response["files"]

        return file_list

    # Helper Functions
    def _colnum_to_colstr(self, colnum):
        colstr = ""
        while colnum > 0:
            colnum, r = divmod(colnum - 1, 26)
            colstr += chr(65 + r)

        return colstr

    def _colstr_to_colnum(self, colstr):
        colnum = 0
        for letter in colstr:
            num = num * 26 + (ord(letter.upper()) - ord("A")) + 1

        return colnum

    def get_spreadsheet_id(self, spreadsheet_name):
        try:
            spreadsheet_id = next(
                file["id"]
                for file in self._file_list
                if file["name"] == spreadsheet_name
            )

        except StopIteration:
            raise Exception("Failed to find file {0} in drive".format(spreadsheet_name))

        return spreadsheet_id

    def clear_sheet(self, spreadsheet_name, sheet_name='Sheet1', by_id=False):
        if by_id:
            spreadsheet_id = spreadsheet_name
        else:
            spreadsheet_id = self.get_spreadsheet_id(spreadsheet_name)

        if isinstance(sheet_name, list):
            for sheet in sheet_name:
                self._sheet_service.spreadsheets().values().batchClear(spreadsheetId=spreadsheet_id, ranges=sheet).execute()

        elif isinstance(sheet_name, str):
            self._sheet_service.spreadsheets().values().batchClear(spreadsheetId=spreadsheet_id, ranges=sheet).execute()

        else:
            raise TypeError("Sheet name variable must be of type str or list")
    
    #Main Functions
    def df_to_sheet(self, df, spreadsheet_name, sheet_name='Sheet1', return_response=False, by_id=False, **kwargs):
        if by_id:
            spreadsheet_id = spreadsheet_name
        else:
            spreadsheet_id = self.get_spreadsheet_id(spreadsheet_name):
        
        sheet_data = [df.columns.values.tolist()] + df.values.tolist()
        colstr = self._colnum_to_colstr(df.shape[1])
        sheet_request_body = {
            "values": sheet_data
        }

        spreadsheet = self.sheet_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        if sheet_name in [sheet["properties"]["title"] for sheet in spreadsheet["sheets"]]:
            self.clear_sheet(spreadsheet_id, by_id=True)

        try:
            sheet_write_request = self._sheet_service.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                                                    range='{0}!A1:{1}{2}'.format(sheet_name, colstr, df.shape[0]+1),valueInputOption=kwargs.get("value_input", "RAW"),body=sheet_request_body,)
            
        except Exception as e:
            print(e)

        else:
            raise Exception("sheet does not exist")

        response = sheet_write_request.execute()

        if return_response:
            return response