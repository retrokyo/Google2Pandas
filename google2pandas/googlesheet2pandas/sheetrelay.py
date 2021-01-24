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
                    pageToken=response['nextPageToken']
                )
                .execute()
            )

            file_list + response["files"]

        return file_list