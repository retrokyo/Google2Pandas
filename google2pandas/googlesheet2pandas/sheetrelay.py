from googleapiclient.discovery import build
from google.oauth2 import service_account

import os

from google2pandas.helpers import ValidateSetterProperty, scope_validation


class SheetRelay:

    sheet_scopes = "https://www.googleapis.com/auth/spreadsheets"
    drive_scopes = "https://www.googleapis.com/auth/drive.readonly"

    def __init__(
        self,
        key_file=None,
    ):
        self.key_file = key_file
        self._sheet_credentials = service_account.Credentials.from_service_account_file(
            self.key_file
        ).with_scopes(sheet_scopes)
        self._drive_credentials = service_account.Credentials.from_service_account_file(
            self.key_file
        ).with_scopes(drive_scopes)
        self._sheet_service = build("sheets", "v4", self._sheet_credentials)
        self._drive_service = build("drive", "v3", self._drive_credentials)
        self._file_list = (
            self.drive_service.files()
            .list(pageSize=1000, q="mimeType='application/vnd.google-apps.spreadsheet'")
            .execute()
        )

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